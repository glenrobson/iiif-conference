#!/bin/bash

if [ -f .apikeys ]; then
    source .apikeys
fi
echo "Running nginx on port 9000: http://localhost"
docker build -t conference:latest . && docker run --rm --name conference -p 9000:9000 -e trello_key=$trello_key -e trello_token=$trello_token conference:latest
