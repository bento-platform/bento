# ensure chord services is at
# /wes/bento_wes/bento_wes
# after container is started so as to allow the volume mount
# to happen first
mv chord_services.json /wes/bento_wes/bento_wes

cd /wes/bento_wes
celery -A bento_wes.app worker --loglevel=INFO &> ./celery.log &

# using 1 worker, 1 thread for compatibility with debugger
gunicorn bento_wes.app:application -w 1 --threads 1 -b 0.0.0.0:${INTERNAL_PORT}