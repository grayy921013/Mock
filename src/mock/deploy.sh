#!/bin/bash
sudo pkill -f 'daphne'
pkill -f 'runworker'
nohup sudo env "PATH=$PATH" daphne mock.asgi:channel_layer --port 80 --bind 0.0.0.0 -v2 &
nohup ./manage.py runworker -v2 &
