#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

ENV_FILE=${SCRIPT_DIR}/app.env

source_env() {
    set -a
    source $ENV_FILE
    set +a
}

run_app() {
    docker-compose up
}

source_env
run_app