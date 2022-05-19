cd ../data;
mkdir db;
mkdir obj;

cd ../chord_drs;
flask db upgrade;

# call variant endpoint to trigger init
cd ..;

# using 1 worker, multiple threads
# see https://stackoverflow.com/questions/38425620/gunicorn-workers-and-threads
gunicorn chord_drs.app:application -w 1 --threads $(expr 2 \* $(nproc --all) + 1) -b 0.0.0.0:${INTERNAL_PORT}
