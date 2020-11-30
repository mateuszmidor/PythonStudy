
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

    if [[ ! -d venv ]]; then 
        # install and initialize virtual env
        sudo $PIP install -U virtualenv  # system-wide install
        virtualenv -p $PYTHON ./venv
        source ./venv/bin/activate 

        # install requirements into newly initialized virtualenv
        $PIP install -r src/requirements.txt
    else
        # just activate virtualenv
        source ./venv/bin/activate
    fi

    echo "Done"
}

function checkWithMyPy() {
    stage "Running mypy"

    mypy --ignore-missing-imports src/ # dont scan 3rd party libraries

    echo "Done"
}

function runProgram() {
    stage "Running program"

    $PYTHON src/main.py

    echo "Done"
}

function runTests() {
    stage "Running unit tests"

    pytest src/

    echo "Done"
}

function tearDown() {
    stage "Tear down"

    deactivate  # virtualenv

    echo "Done"
}

checkPrerequsites
setupVirtualEnv
checkWithMyPy
[[ $1 == "--test" ]] && runTests || runProgram
tearDown