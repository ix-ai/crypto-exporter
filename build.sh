#!/usr/bin/env sh

echo "Setting VERSION='${CI_COMMIT_REF_NAME}-${CI_COMMIT_SHORT_SHA}' in src/constants.py"
echo "VERSION = '${CI_COMMIT_REF_NAME}-${CI_COMMIT_SHORT_SHA}'" >> src/constants.py
