#!/bin/sh
gunicorn --chdir bento_drop_box_service app -w 2 --threads 2 -b 0.0.0.0:5000