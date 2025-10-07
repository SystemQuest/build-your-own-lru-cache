#!/bin/sh
#
# This script is used to run your program on SystemQuest
#
# This runs after .systemquest/compile.sh
#
# Learn more: https://systemquest.dev/program-interface

set -e # Exit on failure

PYTHONPATH=$(dirname $0)/.. exec python3 -m app.main "$@"