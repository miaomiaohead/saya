#!/bin/sh

if [ $# -lt 1 ] ; then
    echo "usage: $0 [ENV]"
    exit 1;
fi

env=$1
container="saya_container_${env}"

exists=`docker container ls -a|grep ${container}`
if [[ -n $exists ]]; then
    r=`docker container stop ${container}`
    echo "stop ${r}"
    r=`docker container rm ${container}`
    echo "rm ${r}"
fi
