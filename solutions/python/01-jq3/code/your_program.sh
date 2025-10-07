#!/bin/sh
#
# Use this script to run your program LOCALLY.
#
# Note: Changing this script WILL NOT affect how SystemQuest runs your program.
#
# Learn more: https://systemquest.dev/program-interface

set -e # Exit early if any commands fail

# Copied from .systemquest/run.sh
#
# - Edit this to change how your program runs locally
# - Edit .systemquest/run.sh to change how your program runs remotely
PYTHONPATH=$(dirname $0) exec python3 -m app.main "$@"
