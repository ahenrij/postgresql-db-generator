#!/bin/bash

set -e

docker run -d \
     --name demodb \
     --env-file .env \
     -p 127.0.0.1:5432:5432 \
     postgres:16.1-alpine