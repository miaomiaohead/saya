#!/bin/sh
# sh run.sh sc_server_image sc_server_container formal ./logs 5003 5003

if [ $# -lt 5 ] ; then
    echo "usage: $0 [IMAGE] [NAME] [ENV] [LOG_PATH] [STATISTICS_PATH] [PORT] [RUNC_PORT]"
    exit 1;
fi

image=$1
name=$2
env=$3
log_path=`readlink -f $4`
statistics_path=`readlink -f ${5}`
port=$6
runc_port=$7

if [ $env != "test" ] && [ $env !=  "prod" ] ; then
    echo "env '${env}' not support"
    exit 1
fi

if [ ! -d ${log_path} ]; then
    echo "log path not exits, path: ${log_path}"
    exit 1
fi

if [ ! -d ${statistics_path} ]; then
    echo "statistics path not exits, path: ${statistics_path}"
    exit 1
fi

docker run -d -p ${port}:${runc_port} \
    -v ${log_path}:/usr/logs \
    -v ${statistics_path}:/usr/statistics \
    -v /etc/localtime:/etc/localtime:ro \
    --name ${name} \
    --env SERVER_ENV=${env} \
    ${image} \
    python entry.py --workers 8 --port ${runc_port}