#!/bin/sh

uvicorn src.app:app --reload --host 0.0.0.0 --port 1337
