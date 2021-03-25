cd ../data;
mkdir db;
mkdir obj;
cd ../chord_drs;
flask db upgrade;
flask run --host=0.0.0.0;