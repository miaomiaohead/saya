#!/bin/sh

if [ $# -lt 1 ] ; then
    echo "usage: $0 [ENV] [PORT:5005] [option:RUNC_PORT]"
    exit 1;
fi

env=$1
port=${2-5005}
runc_port=${3-$port}

image="saya_image"
container="saya_container_${env}"
log_path=`readlink -f ../../server/logs` 
statistics_path=`readlink -f ../../server/statistics`

# build image
echo "===================== 1. build image: ${image} ====================="
pushd ../../server/docker
sh build.sh ${image}
popd

# kill old container
echo "===================== 2. remove container: ${container} ====================="
exists=`docker container ls -a|grep ${container}`
if [[ -n $exists ]]; then
    r=`docker container stop ${container}`
    echo "stop ${r}"
    r=`docker container rm ${container}`
    echo "rm ${r}"
fi

# run container
echo "===================== 3. run container: ${container} ====================="
sh run.sh ${image} ${container} ${env} ${log_path} ${statistics_path} ${port} ${runc_port}
