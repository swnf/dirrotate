FROM alpine:3.12

RUN apk add --no-cache python3 libmagic && \
    apk add --no-cache --virtual .build-deps py3-pip && \
    pip3 install inotify exif python-magic && \
    apk del --no-cache .build-deps && \
    rm -rf /root/.cache

ADD dirrotate.py /dirrotate.py

VOLUME ["/mnt"]
ENTRYPOINT ["/dirrotate.py"]
