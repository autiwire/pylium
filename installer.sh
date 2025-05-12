#!/bin/bash

# get the path of my python modules
my_dir=$(dirname "$0")
my_py_path="$my_dir/src"

# run the installer
PYTHONPATH=$my_py_path python3 -m pylium.core.installer "$@"
