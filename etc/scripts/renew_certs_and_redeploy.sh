#!/bin/bash

# Assuming local.env has BENTO_PROJECT_DIR and BENTO_USER_GROUP set
source ../../local.env

if [[ -z $BENTO_PROJECT_DIR ]]; then
    echo "Please set the BENTO_PROJECT_DIR variable in local.env"
    exit 1
fi

if [[ -z $BENTO_USER_GROUP ]]; then
    echo "Please set the BENTO_USER_GROUP variable in local.env"
    exit 1
fi

cd $BENTO_PROJECT_DIR  && source env/bin/activate ;

# Gateway is always renewed
SERVICES=(gateway)

# Auth needs cert renewal when internal only
if [[ $BENTOV2_USE_EXTERNAL_IDP -eq 0 ]]; then
    echo "Uses internal IDP, will attemps auth certs renewal."
    # Append auth to list of services to renew
    SERVICES+=(auth)
fi

# auth
for SERVICE_NAME in $SERVICES
do

  ./bentoctl.bash clean "$SERVICE_NAME"

  LOCAL_CERTS=$BENTO_PROJECT_DIR/certs/$SERVICE_NAME
  LOCAL_LE=$LOCAL_CERTS/letsencrypt


  sudo docker run -it --rm --name certbot -v "$LOCAL_LE:/etc/letsencrypt" -v "$LOCAL_LE/lib:/var/lib/letsencrypt" -p 80:80 -p 443:443 certbot/certbot renew --dry-run
  sudo docker run -it --rm --name certbot -v "$LOCAL_LE:/etc/letsencrypt" -v "$LOCAL_LE/lib:/var/lib/letsencrypt" -p 80:80 -p 443:443 certbot/certbot renew --force-renewal

  sudo chown -R $BENTO_USER_GROUP:$BENTO_USER_GROUP $LOCAL_CERTS

  ./bentoctl.bash run "$SERVICE_NAME"

done
