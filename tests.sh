#!/bin/sh
# author: deadc0de6 (https://github.com/deadc0de6)
# Copyright (c) 2019, deadc0de6

set -ev

pycodestyle *.py
pyflakes *.py

