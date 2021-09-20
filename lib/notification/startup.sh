cd bento_notification_service
flask db upgrade

# flask run --host=0.0.0.0
cd ..
gunicorn bento_notification_service.app:application -w 1 --threads $(expr 2 \* $(nproc --all) + 1) -b 0.0.0.0:${INTERNAL_PORT}
