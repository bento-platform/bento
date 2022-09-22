#!/bin/sh
cd bento_service_registry/
gunicorn bento_service_registry.app:application -w 1 --threads $(expr 2 \* $(nproc --all) + 1) -b 0.0.0.0:${INTERNAL_PORT}