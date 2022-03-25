#!/bin/sh

find . -name '*.py' -print0 | xargs -0 yapf --diff
