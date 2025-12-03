upstream garage {
  server ${BENTO_GARAGE_CONTAINER_NAME}:${BENTO_GARAGE_S3_API_PORT};
}

server {
  server_name ${BENTO_GARAGE_DOMAIN};

  include /gateway/conf.d/server_config_${BENTO_GATEWAY_USE_TLS}.conf;
  include /gateway/conf.d/ssl_config_${BENTO_GATEWAY_USE_TLS}.conf;

  ssl_certificate ${BENTO_GATEWAY_INTERNAL_GARAGE_FULLCHAIN_RELATIVE_PATH};
  ssl_certificate_key ${BENTO_GATEWAY_INTERNAL_GARAGE_PRIVKEY_RELATIVE_PATH};

  client_max_body_size 0;  # No limit for S3 object uploads

  location / {
    include /gateway/conf.d/proxy_config.conf;
    proxy_pass http://garage;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
