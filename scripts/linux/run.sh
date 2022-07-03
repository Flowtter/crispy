#!/bin/sh

uvicorn app:app --reload --host 0.0.0.0 --port 1337
google-chrome frontend/index.html
