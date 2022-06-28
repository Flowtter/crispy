#!/bin/sh

find backend -name '*.py' -print0 | xargs -0 yapf --diff
