#!/bin/sh
gunicorn bento_beacon.app:app -w 1 --threads $(expr 2 \* $(nproc --all) + 1) -b 0.0.0.0:${BEACON_INTERNAL_PORT}