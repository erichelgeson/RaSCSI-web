#!/usr/bin/env bash
set -e

# verify packages installed
if ! command -v genisoimage &> /dev/null ; then
    echo "genisoimage could not be found"
    echo "Run 'sudo apt install genisoimage' to fix."
    exit 1
fi
if ! command -v python3 &> /dev/null ; then
    echo "python3 could not be found"
    echo "Run 'sudo apt install python3' to fix."
    exit 1
fi
if ! python3 -m venv --help &> /dev/null ; then
    echo "venv could not be found"
    echo "Run 'sudo apt install python3-venv' to fix."
    exit 1
fi

if ! test -e venv; then
  echo "Creating python venv for web server"
  python3 -m venv venv
  echo "Activating venv"
  source venv/bin/activate
  echo "Installing requirements.txt"
  pip install -r requirements.txt
  git rev-parse HEAD > current
fi

source venv/bin/activate

# Detect if someone updates - we need to re-run pip install.
if ! test -e current; then
  git rev-parse > current
else
  if [ "$(cat current)" != "$(git rev-parse HEAD)" ]; then
      echo "New version detected, updating requirements.txt"
      pip install -r requirements.txt
      git rev-parse HEAD > current
  fi
fi

echo "Starting web server..."
python3 web.py