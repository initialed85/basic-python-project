#!/bin/bash

# things you may want to change
BASE_NAME='basic_project'
TIMEZONE='Australia/Perth'

# things you probably don't want to chnage
BASE_IMAGE="${BASE_NAME}_base"
TEST_IMAGE="${BASE_NAME}_${INTERPRETER}"
TEST_CONTAINER="${TEST_IMAGE}_instance"

echo -e "running tests for python"
SAVE_OUTPUT=1 INTERPRETER=python ./test.sh 1>/dev/null 2>&1
cat /tmp/${BASE_NAME}_python_instance

echo -e "\nrunning tests for python3"
SAVE_OUTPUT=1 INTERPRETER=python3 ./test.sh 1>/dev/null 2>&1
cat /tmp/${BASE_NAME}_python3_instance

echo -e "\nrunning tests for pypy"
SAVE_OUTPUT=1 INTERPRETER=pypy ./test.sh 1>/dev/null 2>&1
cat /tmp/${BASE_NAME}_pypy_instance

echo -e "\nrunning tests for pypy3"
SAVE_OUTPUT=1 INTERPRETER=pypy3 ./test.sh 1>/dev/null 2>&1
cat /tmp/${BASE_NAME}_pypy3_instance
