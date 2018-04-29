# basic-python-project
A basic Python project including containerized units tests for Python Python3, PyPy and PyPy3.

# What is it?

An example Python project for a very simple use-case of getting a [Fortune](https://en.wikipedia.org/wiki/Fortune_(Unix)) from an API on the internet.

It includes unit tests and some Docker tooling to run those unit tests for Python, Python3, PyPy and PyPy3.

# Why?

Using Docker test environments in this way has a number of advantages:

* Permits non-Linux users to test their code on Linux (as long as they can run Docker)
* Ensure you don't litter your dev machine with various dependencies
    * Obviously Python virtualenv is a good way to manage this natively, but it falls over as you soon as you have system-level libraries required by the Python libraries
* Ensures your code runs on all the common Python interpreters
* If your production environment is containerized, it means your test environment is now a lot closer to your production environment (less chance of unexpected behaviours)

# How do I use it?

To simply observe the process, the requirements are:

* [Docker](https://www.docker.com/community-edition#/download)

If you extend this repo into your own project and want to upload your Python package to [PyPI](https://pypi.org/), the requirements are:

* [python](https://www.python.org/) (e.g. `brew install python3` for MacOS or `apt-get install python3`)
* [pip](https://pypi.org/project/pip/) (e.g. `brew install pip3` for MacOS or `apt-get install python-pip3` for Ubuntu)
* [twine](https://pypi.org/project/twine/) (e.g. `pip3 install twine`)

Though I recommend you keep these sorts of things confined to a [virtualenv](https://virtualenv.pypa.io/en/stable/) rather than install them natively on your system.

## To run the tests for the default interpreter (Python3)

    ./test.sh

At this point, the following things have happened:

* A Python3 test container was built
* The files required to test were copied into the container
* the JUnit XML test results have been copied onto your machine (in `test_results`)
* your terminal is holding a return code reflecting the return code of the tests (e.g. `echo $?` will return `0` if the tests returned `0`)

## Run the tests for a specific interpeter

Specify the desired interpreter in the `INTERPRETER` environment variable (options are `python`, `python3`, `pypy` and `pypy3`)

    INTERPRETER=pypy ./test.sh

## Run a specific test file/folder

A test file/folder to focus on can be specified as the first command line argument

    ./test.sh tests/fortune_test.py

## To run all tests

    ./test_all.sh

## How does it work?

* A base Ubuntu:16.04 Docker image is described in `Dockerfile_base`
    * The reason for this is that if you need to deal with any system-level requirements, you can handle the install/build of them here and those changes will be carried forward into the other Dockerfiles
* There is a Dockerfile for each interpreter supported (e.g. `Dockerfile_python2`); these extend the base image and contain the steps to install the interpreter and move in the files required for testing
* `test.sh` does the following:
    * build the base container (quick if it's already built)
    * build the container for the specified interpreter (also quick if it's already built)
    * run the tests and get the output

## What should I be aware of?

* The files required for testing are copied in using the `ADD` keyword (rather than using Docker volumes); this is intentional and makes this test process workable for CI systems that are already running in containers (but have access to the host's `docker` executable)
* If you make a change to the source code, the `ADD` command will be run again next build
* If you make a change to `requirements.txt` or `requirements-dev.txt`, the `ADD` commands will be run again next build along with any commands below those commands (standard Docker stuff)

## Let's say I've built my Python package- how do I distribute it (via PyPI)?

You'll need to make sure you have `twine` installed; and you'll need to create a user at PyPI. Once you've done that, create a file called `~/.pypirc` with the following contents:

    [distutils]
    index-servers =
        pypi

    [pypi]
    username: (your username)
    password:  (your password)

Then build a `setup.py` like the one in this repo; important parts of that file are:

* name and description
* author details
* license (it's understood that if a license isn't specified, legally that package is commercially-licensed and may not be used)
* version (cannot re-upload a package if that version has already been uploaded- need to increment)

Finally, run the following commands (you may be able to ommit some of them- doesn't do any harm to leave them):

    python setup.py build
    python setup.py sdist
    python setup.py bdist_wheel
    twine upload dist/*

At this point, your package should now be publish to PyPI.