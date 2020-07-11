#!/bin/sh

if [ $# -lt 5 ] ; then
    echo "usage: $0 [NAME] [CONF] [DATA] [PORT] [PASSWORD]"
    exit 1;
fi

name=$1
mysql_conf=`readlink -f ${2}`
mysql_data=`readlink -f ${3}`
port=$4
password=$5

if [ ! -f ${mysql_conf} ]; then
    echo "conf file not exits, path: ${mysql_conf}"
    exit 1
fi

if [ ! -d ${mysql_data} ]; then
    echo "data dir not exits, path: ${mysql_data}"
    exit 1
fi

docker run -d --name $name \
    -p ${port}:3306 \
    -v ${mysql_conf}:/etc/mysql/conf.d/mysqld.cnf \
    -v ${mysql_data}:/var/lib/mysql \
    -v /etc/localtime:/etc/localtime:ro \
    -e MYSQL\_ROOT\_PASSWORD=${password} \
    mysql:5.6
