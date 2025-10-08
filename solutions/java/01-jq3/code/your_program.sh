#!/bin/sh
#
# Use this script to run your program LOCALLY.
#
# Note: Changing this script WILL NOT affect how SystemQuest runs your program.
#
# Learn more: https://systemquest.dev/program-interface

set -e # Exit early if any commands fail

# Copied from .systemquest/compile.sh
#
# - Edit this to change how your program compiles locally
# - Edit .systemquest/compile.sh to change how your program compiles remotely
(
  cd "$(dirname "$0")" # Ensure compile steps are run within the repository directory
  mvn -q -B package -Ddir=/tmp/systemquest-build-lru-cache-java
)

# Copied from .systemquest/run.sh
#
# - Edit this to change how your program runs locally
# - Edit .systemquest/run.sh to change how your program runs remotely
exec java -jar /tmp/systemquest-build-lru-cache-java/systemquest-lru-cache.jar "$@"
