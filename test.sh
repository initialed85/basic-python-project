#!/bin/bash

# things you may want to change
BASE_NAME='basic_project'
TIMEZONE='Australia/Perth'

# default interpreter is Python3 if not specified in the environment
if [ -z "$INTERPRETER" ]; then
    INTERPRETER="python3"
fi

# things you probably don't want to chnage
FOCUS="$1"
BASE_DOCKERFILE="Dockerfile_base"
BASE_IMAGE="${BASE_NAME}_base"
TEST_DOCKERFILE="Dockerfile_${INTERPRETER}"
TEST_IMAGE="${BASE_NAME}_${INTERPRETER}"
TEST_CONTAINER="${TEST_IMAGE}_instance"
TEST_STDOUT_AND_STDERR="/tmp/${TEST_CONTAINER}"
TEST_RESULTS="${INTERPRETER}_junit_results.xml"

echo -e "building $BASE_IMAGE"
docker build -f $BASE_DOCKERFILE -t $BASE_IMAGE --build-arg TIMEZONE="$TIMEZOME" $EXTRA_BUILD_ARGS .

echo -e "\nbuilding $TEST_IMAGE"
docker build -f $TEST_DOCKERFILE -t $TEST_IMAGE $EXTRA_BUILD_ARGS .

echo -e "\nrunning $TEST_CONTAINER"
if [[ "$SAVE_OUTPUT" == "1" ]]; then 
    docker run -t --name $TEST_CONTAINER $TEST_IMAGE \
        test_python -m pytest -v --junitxml=test_results/$TEST_RESULTS $FOCUS > $TEST_STDOUT_AND_STDERR 2>&1 || false
    TEST_RETURN=$?
else
    docker run -t --name $TEST_CONTAINER $TEST_IMAGE \
        test_python -m pytest -v --junitxml=test_results/$TEST_RESULTS $FOCUS || false
    TEST_RETURN=$?
fi

mkdir -p test_results
rm -f test_results/$TEST_RESULTS
echo -e "\ngetting junit_results.xml from $TEST_CONTAINER"
docker cp $TEST_CONTAINER:/workspace/test_results/$TEST_RESULTS test_results/$TEST_RESULTS
ls -al test_results/$TEST_RESULTS

echo -e "\nremoving $TEST_CONTAINER container"
docker rm $TEST_CONTAINER 2>/dev/null

echo -e "\ndone"

# return the errorlevel of the test command
exit $TEST_RETURN
