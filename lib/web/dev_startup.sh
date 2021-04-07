echo "-- Initializing BentoV2 Web Container [ DEV ].. --";
rm -rf package-lock.json npm-shrinkwrap.json node_modules && 
    npm cache clean --force && 
    npm cache verify && 
    npm install --unsafe-perm=true --allow-root;
echo "-- Building node.. --";
npm run watch &
echo "-- Toggling nginx daemon : off --";
nginx -g 'daemon off;'