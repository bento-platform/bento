#! /usr/bin/env bash

# Set absolute script dir, allows to find absolute project dir & env files
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Removing "/etc/scripts" suffix gives project dir
BENTO_PROJECT_DIR="${SCRIPT_DIR%%/etc/scripts}"

# CD to project dir and source env config
cd $BENTO_PROJECT_DIR && source etc/default_config.env && source local.env;

# Activate python venv
source env/bin/activate

# Init services array, gateway is always renewed
SERVICES=('gateway')

# Auth needs cert renewal when internal only
if [[ $BENTOV2_USE_EXTERNAL_IDP -eq 0 ]]; then
    echo "Uses internal IDP, will attempt auth certs renewal."
    # Append auth to list of services to renew
    SERVICES+=('auth')
fi

# Clean and renew service certs
for SERVICE_NAME in "${SERVICES[@]}"
do

  ./bentoctl.bash clean "$SERVICE_NAME"

  LOCAL_CERTS=$BENTO_PROJECT_DIR/certs/$SERVICE_NAME
  LOCAL_LE=$LOCAL_CERTS/letsencrypt


  docker run -it --rm --name certbot -v "$LOCAL_LE:/etc/letsencrypt" -v "$LOCAL_LE/lib:/var/lib/letsencrypt" -p 80:80 -p 443:443 certbot/certbot renew --dry-run
  docker run -it --rm --name certbot -v "$LOCAL_LE:/etc/letsencrypt" -v "$LOCAL_LE/lib:/var/lib/letsencrypt" -p 80:80 -p 443:443 certbot/certbot renew --force-renewal
  
  sudo chown -R $BENTO_UID:$BENTO_UID $LOCAL_CERTS
done

# Redeploy services with updated certs
for SERVICE_NAME in "${SERVICES[@]}"
do
  ./bentoctl.bash run "$SERVICE_NAME"
done
