#!/usr/bin/env sh

echo "Setting VERSION"
find . -name .git -type d -prune -o -type f -name constants.py -exec sed -i s/^VERSION.*/VERSION\ =\ \'${CI_COMMIT_REF_NAME}\'/g {} + -exec grep VERSION {} +
echo "Setting BUILD"
find . -name .git -type d -prune -o -type f -name constants.py -exec sed -i s/^BUILD.*/BUILD\ =\ \'${CI_COMMIT_SHORT_SHA}\'/g {} + -exec grep BUILD {} +
