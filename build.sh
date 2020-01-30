#!/usr/bin/env sh

echo "Setting VERSION='${CI_COMMIT_REF_NAME}-${CI_COMMIT_SHORT_SHA}'"
find . -name .git -type d -prune -o -type f -name constants.py -exec sed -i '' s/^VERSION.*/VERSION\ =\ \'${CI_COMMIT_REF_NAME}\'/g {} +
find . -name .git -type d -prune -o -type f -name constants.py -exec sed -i '' s/^BUILD.*/BUILD\ =\ \'${CI_COMMIT_SHORT_SHA}\'/g {} +
