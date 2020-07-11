#!/bin/sh

if [ $# -lt 1 ] ; then
    echo "usage: $0 [IMAGE]"
    exit 1;
fi

image=$1
docker build -t ${image} -f ./Dockerfile ..
