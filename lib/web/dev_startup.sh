echo "-- Initializing BentoV2 Web Container [ DEV ].. --";
cd bento_web;

chown -R $BENTO_WEB_USER dist
chgrp -R $BENTO_WEB_USER dist

echo "-- Toggling nginx daemon : off --"
nginx -g 'daemon off;' &

# Removing the ampersand from the following line will prevent webpack output
# to be streamed to stdout
echo "-- Running `npm run watch`.. --" &
npm run watch