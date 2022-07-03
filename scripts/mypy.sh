#!/bin/sh

find backend/src/crispy -name '*.py' -print0 | xargs -0 mypy \
    --python-version 3.8 \
    --disallow-untyped-calls \
    --disallow-untyped-defs \
    --disallow-incomplete-defs \
    --no-implicit-optional \
    --allow-redefinition \
    --show-error-context \
    --show-column-numbers \
    --pretty
