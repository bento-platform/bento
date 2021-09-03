#!/bin/sh
# using 1 worker, multiple threads
# see https://stackoverflow.com/questions/38425620/gunicorn-workers-and-threads
gunicorn bento_variant_service.wsgi:application -w 1 --threads $(expr 2 \* $(nproc --all) + 1) -b 0.0.0.0:${INTERNAL_PORT}