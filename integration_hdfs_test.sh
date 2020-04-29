#!/bin/bash
set -o allexport
export INTEGRATION_TEST_METHOD_NAME=$1
export INTEGRATION_TEST_USERNAME=$2
export INTEGRATION_TEST_SECRET_KEY=$3
export INTEGRATION_TEST_HDFS_URI=$4

if [ "$5"  != "" ]
then
    export INTEGRATION_TEST_FILEPATH=$5
fi

if [ "$6" !=  "" ]
then
    export INTEGRATION_TEST_SCHEMA_PATH=$6
fi

export SKIP_INTEGRATION_TESTS=False

python manage.py test methodmapping.tests.test_integration
set +o allexport
