echo "-- Initializing BentoV2 Web Container [ PROD ].. --";
cd bento_web;

echo "-- Building node.. --";
npm run build -y;

echo "-- Toggling nginx daemon : off --";
nginx -g 'daemon off;'

