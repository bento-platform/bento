echo "-- Initializing BentoV2 Web Container [ DEV ].. --";
cd bento_web;

chown -R $BENTO_WEB_USER dist
chgrp -R $BENTO_WEB_USER dist

echo "-- Running `npm run watch`.. --";
npm run watch &

echo "-- Toggling nginx daemon : off --";
nginx -g 'daemon off;'