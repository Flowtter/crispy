#!/bin/sh

find backend/src -name '*.py' -print0 | xargs -0 pylint --load-plugins pylint_quotes
