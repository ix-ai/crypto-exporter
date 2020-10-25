#!/usr/bin/env sh

set -xeu

if [ -n "${CI_PIPELINE_ID:-}" ]; then
  sed -i "s|^BUILD.*|BUILD = '${CI_PIPELINE_ID}'|g" exporter/lib/constants.py
fi
