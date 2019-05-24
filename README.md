# dirrotate

Dirrotate is a small application which continuously monitors a directory for new files and moves them to a monthly archive directory after a specific timespan. It uses the exif time (if present) or mtime to decide how old a file is. You can also use it together with file synchronization software like Syncthing to remove old pictures from your mobile.

docker-compose example (`base-directory/current` will be monitored):

```
version: "3"
services:
  dirrotate:
    image: dirrotate
    restart: always
    environment:
      - 'TZ=Europe/Berlin'
    volumes:
      - 'base-directory:/mnt'
      - '/usr/share/zoneinfo:/usr/share/zoneinfo:ro'
```

**Important note**: Dirrotate just waits three seconds after it detects a new file before reading it. Especially if dirrotate moves those new files immediately, they might be incomplete.
