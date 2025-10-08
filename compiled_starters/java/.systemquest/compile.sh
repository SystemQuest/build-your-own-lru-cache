#!/bin/sh
#
# This script is used to compile your program on SystemQuest
#
# This runs before .systemquest/run.sh
#
# Learn more: https://systemquest.dev/program-interface

set -e # Exit on failure

mvn -q -B package -Ddir=/tmp/systemquest-build-lru-cache-java
