cd ../data;
mkdir db;
mkdir obj;
cd ../chord_drs;
flask db upgrade;
flask run --host=0.0.0.0;

echo "sleeping for 5 seconds";
sleep 5;

# call variant endpoint to trigger init
URL=$VARIANT_SERVICE_URL/private/post-start-hook
echo "calling $URL";
curl $URL