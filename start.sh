#!/usr/bin/env bash

# verify packages installed
# python3-venv, iso utility, etc

if ! test -e venv; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

python3 web.py