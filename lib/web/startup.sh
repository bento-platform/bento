echo "-- Initializing BentoV2 Web Container [ PROD ].. --";

echo "-- Building node.. --";
npm run build;

echo "-- Toggling nginx daemon : off --";
nginx -g 'daemon off;'
