echo "-- Initializing BentoV2 Web Container [ DEV ].. --";

echo "-- Running `npm run watch`.. --";
npm run watch &

echo "-- Toggling nginx daemon : off --";
nginx -g 'daemon off;'