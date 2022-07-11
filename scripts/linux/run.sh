#!/bin/sh

google-chrome frontend/index.html
uvicorn app:app --reload --host 127.0.0.1 --port 1337
