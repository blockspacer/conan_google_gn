#!/usr/bin/env bash
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"
export PATH="${JAVA_HOME}/bin${PATH:+":${PATH}"}"
export LD_LIBRARY_PATH="${JAVA_HOME}/jre/lib/amd64/server${LD_LIBRARY_PATH:+":${LD_LIBRARY_PATH}"}"