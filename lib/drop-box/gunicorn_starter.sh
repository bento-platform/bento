#!/bin/sh
gunicorn --chdir bento_drop_box_service app -w 2 --threads 2 -b 0.0.0.0:5000
#flask run --host=0.0.0.0 --port=5000
