# env: BENTO_MINIO_ENABLED
location /api/minio { return 302 https://${BENTOV2_DOMAIN}/api/minio/; }
location /api/minio/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # proxy_set_header Connection "";
    proxy_connect_timeout 300;
    chunked_transfer_encoding off;

    # Forward request to event-relay
    rewrite ^ $request_uri;
    rewrite ^/api/event-relay/(.*) /$1 break;
    return 400;

    proxy_pass http://${BENTO_MINIO_CONTAINER_NAME}:${BENTO_MINIO_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_minio_errors.log;    
}

location /api/minio-console { return 302 https://${BENTOV2_DOMAIN}/api/minio-console/; }
location /api/minio-console/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;    

    real_ip_header X-Real-IP;
    proxy_set_header X-NginX-Proxy true;
    proxy_connect_timeout 300;
    chunked_transfer_encoding off;    
    
    # Forward request to event-relay
    rewrite ^ $request_uri;
    rewrite ^/api/minio-console/(.*) /$1 break;
    proxy_pass http://${BENTO_MINIO_CONTAINER_NAME}:${BENTO_MINIO_CONSOLE_PORT}$uri;    

    # Add sub_filter directives to rewrite base href
    sub_filter '<base href="/"' '<base href="/api/minio-console/"';
    sub_filter_once on;

    # Ensure sub_filter module is enabled
    proxy_set_header Accept-Encoding "";    

    # Errors
    error_log /var/log/bentov2_minio_errors.log;        
}