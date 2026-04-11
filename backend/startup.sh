#!/bin/bash
set -e

gunicorn -w 2 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:${PORT:-8000} app.main:app
