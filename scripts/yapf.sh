#!/bin/sh

find src -name '*.py' -print0 | xargs -0 yapf --diff
