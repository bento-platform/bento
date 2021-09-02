#!/bin/sh
gunicorn --chdir bento_service_registry app -w 2 --threads 2 -b 0.0.0.0:5000