
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
        sudo $PIP install -U virtualenv  # system-wide install
        virtualenv --system-site-packages -p $PYTHON ./venv
        #   $PIP install --user matplotlib
    fi

    source ./venv/bin/activate # virtualenv

    echo "Done"
}

function runProgram() {
    stage "Running program"

    $PYTHON src/main.py

    echo "Done"
}

function tearDown() {
    stage "Tear down"

    deactivate  # virtualenv

    echo "Done"
}

checkPrerequsites
setupVirtualEnv
runProgram
tearDown