FROM python:3.6-alpine

RUN mkdir /dccron
ADD requirements.txt /dccron/requirements.txt
WORKDIR /dccron

RUN apk update&&apk add --no-cache build-base jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev&& apk add --no-cache mariadb-connector-c-dev&&pip --no-cache-dir install -r requirements.txt&& apk del build-base

EXPOSE 80
ENV TZ "Asia/Shanghai"

ENV DBNAME dccron
ENV DBUSER dccron
ENV DBPASS dccron
ENV DBHOST localhost
ENV DBPORT 3306


RUN apk add nginx&&mkdir /run/nginx

ADD default.conf /etc/nginx/conf.d/default.conf

ADD dccron/settings.py.conf /dccron/dccron/settings.py

ENV DCINIT 0
ADD . /dccron/

CMD ["/bin/sh","start.sh","$DCINIT"]