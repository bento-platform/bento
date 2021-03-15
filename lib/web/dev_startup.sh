rm -rf package-lock.json npm-shrinkwrap.json node_modules && 
    npm cache clean --force && 
    npm cache verify && 
    npm install --unsafe-perm=true --allow-root;
npm run watch &
nginx -g 'daemon off;'