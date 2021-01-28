cd ..;
celery -A bento_wes.app worker &> ./celery.log &
cd ./bento_wes;
flask run --host=0.0.0.0;