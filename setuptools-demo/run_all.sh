
#!/usr/bin/env bash

trap tearDown SIGINT

PYTHON=python3
PIP=pip3

function stage() {
    BOLD_BLUE="\e[1m\e[34m"
    RESET="\e[0m"
    msg="$1"
    
    echo
    echo -e "$BOLD_BLUE$msg$RESET"
}

function checkPrerequsites() {
    stage "Checking prerequisites"

    command $PYTHON --version > /dev/null 2>&1
    [[ $? != 0 ]] && echo "You need to install python3 to run this program" && exit 1

    command $PIP --version > /dev/null 2>&1
    [[ $? != 0 ]] && echo "You need to install pip3 to run this program" && exit 1

    echo "Done"
}

function setupVirtualEnv() {
    stage "Setting up virtualenv"

    # install and initialize virtual env
    sudo $PIP install -U virtualenv  # system-wide install
    virtualenv --system-site-packages -p $PYTHON ./venv
    source ./venv/bin/activate 

    echo "Done"
}

function installPackageWithPip() {
    stage "installing setuptools-demo package"

    $PIP install . # install current package defined by setup.py

    echo "Done"
}

function runProgram() {
    stage "Running newly installed tool"

    # run it as shell command (NOTE: only available in virtualenv where installe)
    setuptools-demo

    echo "Done"
}

function tearDown() {
    stage "Tear down"

    deactivate  # virtualenv
    rm -rf venv

    echo "Done"
}

checkPrerequsites
setupVirtualEnv
installPackageWithPip
runProgram
tearDown