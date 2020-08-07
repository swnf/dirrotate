#!/usr/bin/env python3

from pathlib import Path
import sched
import signal
from time import strftime, localtime, time, sleep, mktime, strptime
from exif import Image
from inotify.adapters import Inotify
import magic

i = Inotify()
i.add_watch('/mnt/current')
s = sched.scheduler(time)

signal.signal(signal.SIGTERM, signal.default_int_handler)


def get_creation_time(file):
    if magic.from_file(str(file), mime=True).startswith('image/'):
        try:
            with file.open('rb') as content:
                exif = Image(content)
                return mktime(strptime(exif.datetime, "%Y:%m:%d %H:%M:%S"))
        except:
            return file.stat().st_mtime
    else:
        return file.stat().st_mtime


def do_move(file):
    creation_time = get_creation_time(file)
    directory = strftime('%Y-%m', localtime(creation_time))
    Path('/mnt/' + directory).mkdir(exist_ok=True)
    print('moving ' + file.name + ' to ' + directory, flush=True)
    file.rename('/mnt/' + directory + '/' + file.name)


def register(file):
    if file.name.startswith('.') or file.is_dir():
        return
    if not [item for item in s.queue if item[3] == (file, )]:
        sleep(3)
        creation_time = get_creation_time(file)
        targettime = creation_time + 3600 * 24 * 30
        print('new file "' + file.name +
              '" not already registered, modification time ' +
              strftime('%Y-%m-%d %H:%M:%S', localtime(creation_time)) +
              ', archive time ' +
              strftime('%Y-%m-%d %H:%M:%S', localtime(targettime)),
              flush=True)
        if time() > targettime:
            do_move(file)
        else:
            print('file move planned', flush=True)
            s.enterabs(targettime, 1, do_move, (file, ))


def unregister(file):
    if [item for item in s.queue if item[3] == (file, )]:
        s.cancel([item for item in s.queue if item[3] == (file, )][0])
        print('file "' + file.name +
              '" not already unregistered, removing from list',
              flush=True)


print('dirrotate started, scanning directory the first time', flush=True)
for f in Path('/mnt/current').iterdir():
    register(f)
print('waiting for changes', flush=True)

try:
    while True:
        for event in i.event_gen():
            if event is not None:
                (header, type_names, watch_path, filename) = event
                if 'IN_CREATE' in type_names or 'IN_MOVED_TO' in type_names:
                    register(Path('/mnt/current') / filename)
                elif 'IN_DELETE' in type_names or 'IN_MOVED_FROM' in type_names:
                    unregister(Path('/mnt/current') / filename)
            s.run(blocking=False)
finally:
    print('clean exit', flush=True)
    i.remove_watch(b'/mnt/current')
