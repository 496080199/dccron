FROM python:3.6-alpine

RUN mkdir /dccron&&mkdir /run/nginx
ADD requirements.txt /dccron/requirements.txt
WORKDIR /dccron

RUN apk update&&apk add --no-cache build-base tzdata jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev libffi-dev&& apk add --no-cache mariadb-connector-c-dev nginx&&pip --no-cache-dir install -r requirements.txt&& apk del build-base&&ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

EXPOSE 80

ENV DBNAME dccron
ENV DBUSER dccron
ENV DBPASS dccron
ENV DBHOST localhost
ENV DBPORT 3306


ADD default.conf /etc/nginx/conf.d/default.conf

ADD dccron/settings.py.conf /dccron/dccron/settings.py

ENV DCINIT 0
ADD . /dccron/

CMD ["/bin/sh","start.sh"]