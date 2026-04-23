#!/bin/bash

echo "Starting setup..."

if ! command -v brew &> /dev/null
then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

if ! command -v python3 &> /dev/null
then
    brew install python
fi

if ! command -v node &> /dev/null
then
    brew install node
fi

npm install -g appium
pip3 install -r requirements.txt

appium &

sleep 5

python3 main.py