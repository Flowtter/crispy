#!/bin/sh

find backend/src/crispy -name '*.py' -print0 | xargs -0 pylint
