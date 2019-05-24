FROM alpine

RUN apk add --no-cache python3 libmagic && pip3 install inotify exif python-magic
ADD dirrotate.py /dirrotate.py

VOLUME ["/mnt"]
ENTRYPOINT ["/dirrotate.py"]
