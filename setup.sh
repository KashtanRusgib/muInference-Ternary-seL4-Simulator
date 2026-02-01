#!/bin/bash
# Setup script for env and deps
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install numpy matplotlib  # If not pre-installed
git submodule update --init --recursive
echo "Setup complete. Run source venv/bin/activate before tests."