#!/bin/sh
#
# This script is used to run your program on SystemQuest
#
# This runs after .systemquest/compile.sh
#
# Learn more: https://systemquest.dev/program-interface

set -e # Exit on failure

exec /tmp/systemquest-build-lru-cache-go "$@"
