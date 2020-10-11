#!/usr/bin/env bash
set -e

# verify packages installed
# python3-venv, iso utility, etc

if ! test -e venv; then
  echo "Creating python venv for web server"
  python3 -m venv venv
fi

source venv/bin/activate

#echo "Checking all requirements are installed"
#pip install -r requirements.txt

echo "Starting web server..."
python3 web.py