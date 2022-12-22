#!bin/bash
IMAGE=symp_code

while getopts "t:h" o; do
    case "${o}" in
        t)
            TAG=${OPTARG}
            ;;
        h)
            echo "sh build -t [TAG NAME]"
            exit 1
    esac
done

IMAGE_URL=${IMAGE}:${TAG}

CUR_DIR=$(cd `dirname $0` && pwd -P)
ROOT_DIR=${CUR_DIR}/../..

mkdir ${CUR_DIR}/tmp
mkdir ${CUR_DIR}/tmp/code
mkdir ${CUR_DIR}/tmp/code/convid_pred
mkdir ${CUR_DIR}/tmp/code/symp_pred

cp ${ROOT_DIR}/*.py ${CUR_DIR}/tmp/code/
cp -r ${ROOT_DIR}/convid_pred ${CUR_DIR}/tmp/code/
cp -r ${ROOT_DIR}/symp_pred ${CUR_DIR}/tmp/code/

docker build --tag ${IMAGE_URL} ${CUR_DIR}

rm -rf ${CUR_DIR}/tmp

exit 0