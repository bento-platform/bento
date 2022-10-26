worker_processes 1;

# expose env's to lua code
env CHORD_DEBUG;
env CHORD_PERMISSIONS;
env CHORD_PRIVATE_MODE;
env CHORD_URL;

env OIDC_DISCOVERY_URI;
env REDIRECT_AFTER_LOGOUT_URI;
env CLIENT_ID;
env TOKEN_ENDPOINT_AUTH_METHOD;

# TODO: move to secret instead of using env
env CLIENT_SECRET;

events {
    worker_connections 1024;
}

http {
    # Use the Docker embedded DNS server
    resolver 127.0.0.11 ipv6=off;

    log_format compression '${DOLLAR}remote_addr - ${DOLLAR}remote_user [${DOLLAR}time_local] '
                            '"${DOLLAR}request" ${DOLLAR}status ${DOLLAR}body_bytes_sent '
                            '"${DOLLAR}http_referer" "${DOLLAR}http_user_agent" "${DOLLAR}gzip_ratio" "${DOLLAR}uri"';

    limit_req_zone ${DOLLAR}binary_remote_addr zone=global_limit:10m rate=10r/s;

    # Redirect all http to https
    server {
        listen 80 default_server;
        listen [::]:80 default_server;

        server_name _; # Redirect http no matter the domain name

        # Security --
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        # --

        return 301 https://${DOLLAR}host${DOLLAR}request_uri;
    }

    # All https traffic
    # -- Internal IDP Starts Here --
    # BentoV2 Auth
    server {
        listen 443 ssl;

        server_name ${BENTOV2_AUTH_DOMAIN};

        ssl_certificate ${BENTOV2_GATEWAY_INTERNAL_CERTS_DIR}${BENTOV2_GATEWAY_INTERNAL_AUTH_FULLCHAIN_RELATIVE_PATH};
        ssl_certificate_key ${BENTOV2_GATEWAY_INTERNAL_CERTS_DIR}${BENTOV2_GATEWAY_INTERNAL_AUTH_PRIVKEY_RELATIVE_PATH};


        # Security --
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        # --

        location / {
            limit_req zone=global_limit burst=10;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            # Keycloak Load-Balancer configuration requirements
            #  see: https://wjw465150.gitbooks.io/keycloak-documentation/content/server_installation/topics/clustering/load-balancer.html
            proxy_set_header X-Forwarded-Proto ${DOLLAR}scheme;
            proxy_set_header X-Forwarded-Host ${DOLLAR}host;
            proxy_set_header X-Forwarded-For ${DOLLAR}proxy_add_x_forwarded_for;
            #

            proxy_ignore_client_abort on;

            set ${DOLLAR}upstream_auth http://bentov2-auth:8080;

            proxy_pass    ${DOLLAR}upstream_auth;
            error_log /var/log/bentov2_auth_errors.log;
        }
    }
    # -- Internal IDP Ends Here --


    # Bento Public
    server {
        listen 443 ssl;

        server_name ${BENTOV2_DOMAIN};

        ssl_certificate ${BENTOV2_GATEWAY_INTERNAL_CERTS_DIR}${BENTOV2_GATEWAY_INTERNAL_FULLCHAIN_RELATIVE_PATH};
        ssl_certificate_key ${BENTOV2_GATEWAY_INTERNAL_CERTS_DIR}${BENTOV2_GATEWAY_INTERNAL_PRIVKEY_RELATIVE_PATH};

        # Security --
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        # --

        # -- Use Bento-Public Starts Here --
        # Public Web
        location / {
            limit_req zone=global_limit burst=10;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            set ${DOLLAR}upstream_public http://${BENTO_PUBLIC_CONTAINER_NAME}:${BENTO_PUBLIC_INTERNAL_PORT};
            proxy_pass    ${DOLLAR}upstream_public;

            error_log /var/log/bentov2_public_errors.log;
        }

        # -- Beacon
        location ~ /api/beacon {
            limit_req zone=global_limit burst=10;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Remove "/api/beacon" from the path
            rewrite /api/beacon/(.*) /${DOLLAR}1  break;

            # Forward request to beacon
            proxy_pass    http://${BEACON_CONTAINER_NAME}:${BEACON_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args; 

            # Errors
            error_log /var/log/bentov2_beacon_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }

        # -- Use Bento-Public Ends Here --
        # -- Do Not Use Bento-Public Starts Here --
        return 301 https://portal.${DOLLAR}host${DOLLAR}request_uri;
        # -- Do Not Use Bento-Public Ends Here --
    }


    # Bento Portal
    server {
        listen 443 ssl;

        server_name ${BENTOV2_PORTAL_DOMAIN};

        ssl_certificate ${BENTOV2_GATEWAY_INTERNAL_CERTS_DIR}${BENTOV2_GATEWAY_INTERNAL_PORTAL_FULLCHAIN_RELATIVE_PATH};
        ssl_certificate_key ${BENTOV2_GATEWAY_INTERNAL_CERTS_DIR}${BENTOV2_GATEWAY_INTERNAL_PORTAL_PRIVKEY_RELATIVE_PATH};

        # Security --
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        # --


        # CHORD constants (configuration file locations)
        set ${DOLLAR}chord_auth_config     "{auth_config}";
        set ${DOLLAR}chord_instance_config "{instance_config}";

        # - Per lua-resty-session, the 'regenerate' strategy is more reliable for
        #   SPAs which make a lot of asynchronous requests, as it does not
        #   immediately replace the old records for sessions when making a new one.
        set ${DOLLAR}session_strategy        regenerate;


        # Web
        location / {
            limit_req zone=global_limit burst=10;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;


            set ${DOLLAR}request_url ${DOLLAR}request_uri;
            set ${DOLLAR}url ${DOLLAR}uri;

            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            access_by_lua_file /usr/local/openresty/nginx/proxy_auth.lua;
            #try_files ${DOLLAR}uri /index.html;

            set ${DOLLAR}upstream_web http://${BENTOV2_WEB_CONTAINER_NAME}:${BENTOV2_WEB_INTERNAL_PORT};

            proxy_pass    ${DOLLAR}upstream_web;
            error_log /var/log/bentov2_web_errors.log;

        }

        # --- All API stuff -- /api/* ---
        # -- Public node-info
        location = /api/node-info {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }
            content_by_lua_file /usr/local/openresty/nginx/node_info.lua;
        }

        # -- User Auth
        location ~ /api/auth {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            content_by_lua_file /usr/local/openresty/nginx/proxy_auth.lua;
        }

        # TODO: De-duplicate api services

        # -- Katsu
        location ~ /api/metadata {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            #proxy_pass           http://unix:/chord/tmp/nginx_internal.sock;

            # Remove "/api/metadata" from the path
            rewrite /api/metadata/(.*) /${DOLLAR}1  break;

            # Forward request to the katsu
            proxy_pass    http://${BENTOV2_KATSU_CONTAINER_NAME}:${BENTOV2_KATSU_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_metadata_errors.log;


            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }


        # -- Drop-Box
        location ~ /api/drop-box {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/drop-box" from the path
            rewrite /api/drop-box/(.*) /${DOLLAR}1  break;

            # Forward request to the drop-box
            proxy_pass  http://${BENTOV2_DROP_BOX_CONTAINER_NAME}:${BENTOV2_DROP_BOX_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_drop_box_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }


        # -- Service-Registry
        location ~ /api/service-registry { # ^~ /api/service-registry/
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/service-registry" from the path
            rewrite /api/service-registry/(.*) /${DOLLAR}1  break;

            # Forward request to the service-registry
            proxy_pass  http://${BENTOV2_SERVICE_REGISTRY_CONTAINER_NAME}:${BENTOV2_SERVICE_REGISTRY_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_service_registry_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }


        # -- Logging
        location ~ /api/log-service {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/log-service" from the path
            rewrite /api/log-service/(.*) /${DOLLAR}1  break;

            # Forward request to the log-service
            proxy_pass  http://${BENTOV2_LOGGING_CONTAINER_NAME}:${BENTOV2_LOGGING_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_logging_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }


        # -- DRS
        location ~ /api/drs {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/drs" from the path
            rewrite /api/drs/(.*) /${DOLLAR}1  break;

            # Forward request to DRS
            proxy_pass  http://${BENTOV2_DRS_CONTAINER_NAME}:${BENTOV2_DRS_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_drs_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }


        # -- Notifications
        location ~ /api/notification {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/notification" from the path
            rewrite /api/notification/(.*) /${DOLLAR}1  break;

            # Forward request to notification service
            proxy_pass  http://${BENTOV2_NOTIFICATION_CONTAINER_NAME}:${BENTOV2_NOTIFICATION_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_notification_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }

        # -- Federation
        location ~ /api/federation {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/federation" from the path
            rewrite /api/federation/(.*) /${DOLLAR}1  break;

            # Forward request to federation service
            proxy_pass  http://${BENTOV2_FEDERATION_CONTAINER_NAME}:${BENTOV2_FEDERATION_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_federation_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }

        # -- Event-Relay
        location ~ /api/event-relay {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/event-relay" from the path
            rewrite /api/event-relay/(.*) /${DOLLAR}1  break;

            # Forward request to event-relay service
            proxy_pass  http://${BENTOV2_EVENT_RELAY_CONTAINER_NAME}:${BENTOV2_EVENT_RELAY_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_event_relay_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }


        # -- WES
        location ~ /api/wes {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/wes" from the path
            rewrite /api/wes/(.*) /${DOLLAR}1  break;

            # Forward request to wes service
            proxy_pass  http://${BENTOV2_WES_CONTAINER_NAME}:${BENTOV2_WES_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_wes_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }
        # ...


        # -- Gohan
        location ~ /api/gohan {
            limit_req zone=global_limit burst=10;
            set_by_lua_block ${DOLLAR}original_uri { return ngx.var.uri }

            # Authentication
            access_by_lua_file   /usr/local/openresty/nginx/proxy_auth.lua;


            proxy_http_version   1.1;

            proxy_pass_header    Server;
            proxy_set_header     Upgrade           ${DOLLAR}http_upgrade;
            proxy_set_header     Connection        "upgrade";
            proxy_set_header     Host              ${DOLLAR}http_host;
            proxy_set_header     X-Real-IP         ${DOLLAR}remote_addr;
            proxy_set_header     X-Forwarded-For   ${DOLLAR}proxy_add_x_forwarded_for;
            proxy_set_header     X-Forwarded-Proto ${DOLLAR}http_x_forwarded_proto;

            proxy_ignore_client_abort on;

            # Clear X-CHORD-Internal header and set it to the "off" value (0)
            proxy_set_header     X-CHORD-Internal  "0";

            # Remove "/api/gohan" from the path
            rewrite /api/gohan/(.*) /${DOLLAR}1  break;

            # Forward request to wes service
            proxy_pass  http://${GOHAN_API_CONTAINER_NAME}:${GOHAN_API_INTERNAL_PORT}/${DOLLAR}1${DOLLAR}is_args${DOLLAR}args;

            # Errors
            error_log /var/log/bentov2_gohan_api_errors.log;

            client_body_timeout  660s;
            proxy_read_timeout   660s;
            proxy_send_timeout   660s;
            send_timeout         660s;

            client_max_body_size 200m;
        }
        # ...
    }
}