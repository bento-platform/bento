upstream garage_s3 {
  server ${BENTO_GARAGE_CONTAINER_NAME}:${BENTO_GARAGE_S3_API_PORT};
}

upstream garage_web {
  server ${BENTO_GARAGE_CONTAINER_NAME}:${BENTO_GARAGE_WEB_PORT};
}

# Main S3 API endpoint (path-style and virtual-hosted-style buckets)
server {
  server_name ${BENTO_GARAGE_DOMAIN} *.s3.${BENTO_GARAGE_DOMAIN};

  include /gateway/conf.d/server_config_${BENTO_GATEWAY_USE_TLS}.conf;
  include /gateway/conf.d/ssl_config_${BENTO_GATEWAY_USE_TLS}.conf;

  ssl_certificate ${BENTOV2_GATEWAY_INTERNAL_FULLCHAIN_RELATIVE_PATH};
  ssl_certificate_key ${BENTOV2_GATEWAY_INTERNAL_PRIVKEY_RELATIVE_PATH};

  client_max_body_size 0;  # No limit for S3 object uploads

  location / {
    include /gateway/conf.d/proxy_config.conf;
    proxy_pass http://garage_s3;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}

# Web interface for static website hosting
server {
  server_name *.web.${BENTO_GARAGE_DOMAIN};

  include /gateway/conf.d/server_config_${BENTO_GATEWAY_USE_TLS}.conf;
  include /gateway/conf.d/ssl_config_${BENTO_GATEWAY_USE_TLS}.conf;

  ssl_certificate ${BENTOV2_GATEWAY_INTERNAL_FULLCHAIN_RELATIVE_PATH};
  ssl_certificate_key ${BENTOV2_GATEWAY_INTERNAL_PRIVKEY_RELATIVE_PATH};

  client_max_body_size 0;

  location / {
    include /gateway/conf.d/proxy_config.conf;
    proxy_pass http://garage_web;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
