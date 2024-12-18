# Deployment

This section details the required steps to deploy Bento on a server and expose it to the internet.
The instructions assume you have a server with a public IP and DNS records pointing to it for the domains you will use.

A bento deployment usually has up to 4 domains or subdomains, this section uses the following examples:
```bash
BENTOV2_DOMAIN=bento.example.com
BENTOV2_PORTAL_DOMAIN=portal.${BENTOV2_DOMAIN}
BENTOV2_AUTH_DOMAIN=auth.${BENTOV2_DOMAIN}
BENTOV2_CBIOPORTAL_DOMAIN=cbioportal.${BENTOV2_DOMAIN}
BENTO_MINIO_DOMAIN=minio.${BENTOV2_DOMAIN}
```

For a real deployment, make sure that your `local.env` file uses valid domain names for which SSL certificates 
can be obtained.

## Certificates paths

In production mode, Bento must use valid SSL certificates instead of self-signed ones.
Before requesting certificates, make sure that you override the following environment 
variables in your `local.env` file.

```bash
BENTOV2_AUTH_FULLCHAIN_RELATIVE_PATH=/live/$BENTOV2_AUTH_DOMAIN/fullchain.pem
BENTOV2_AUTH_PRIVKEY_RELATIVE_PATH=/live/$BENTOV2_AUTH_DOMAIN/privkey.pem
BENTOV2_GATEWAY_INTERNAL_PORTAL_FULLCHAIN_RELATIVE_PATH=/live/$BENTOV2_PORTAL_DOMAIN/fullchain.pem
BENTOV2_GATEWAY_INTERNAL_PORTAL_PRIVKEY_RELATIVE_PATH=/live/$BENTOV2_PORTAL_DOMAIN/privkey.pem
BENTOV2_GATEWAY_INTERNAL_FULLCHAIN_RELATIVE_PATH=/live/$BENTOV2_DOMAIN/fullchain.pem
BENTOV2_GATEWAY_INTERNAL_PRIVKEY_RELATIVE_PATH=/live/$BENTOV2_DOMAIN/privkey.pem
```

## Obtain certificates

On a fresh Bento install, the initial SSL certificates can be obtained with a convenience script.

```bash
bash ./etc/scripts/init_certs_only.sh

# Answer CertBot prompts
# Does a --dry-run first

# Check the certificates
ls ./certs/gateway/letsencrypt
ls ./certs/auth/letsencrypt
```

## Renew certificates

To renew the certificates after they are issued, use the convenience script made to this effect:

```bash
bash ./etc/scripts/renew_certs_and_redeploy.sh
# Answer CertBot prompts
# Does a --dry-run first

# Check the certificates
ls ./certs/gateway/letsencrypt/live
ls ./certs/auth/letsencrypt/live
```

Note that this script will shutdown auth and gateway during the certificate renewal.

## Permanently redirect a domain

If a Bento instance must use a new domain, the gateway can redirect requests from the old domain to the new one. 
This is advised to prevent dead links, see [301](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301) 
response status reference.

For this to work, you **must** update the old domain's DNS record to point to the new instance's IP, 
otherwise you won't be able to obtain the certificates.

First, declare these variables in the `local.env` file:

```bash
BENTO_DOMAIN_REDIRECT=old-bento.example.com     # The old domain name
BENTO_USE_DOMAIN_REDIRECT='true'                # Feature flag for domain redirect
BENTO_GATEWAY_INTERNAL_REDIRECT_FULLCHAIN_RELATIVE_PATH=/live/$BENTO_DOMAIN_REDIRECT/fullchain.pem
BENTO_GATEWAY_INTERNAL_REDIRECT_PRIVKEY_RELATIVE_PATH=/live/$BENTO_DOMAIN_REDIRECT/privkey.pem
```

Obtain the certificate for the old domain with certbot:
```bash
# Stop gateway
./bentoctl.bash stop gateway

# Obtain certificates
docker run -it --rm --name certbot \
    -v "./certs/gateway/letsencrypt:/etc/letsencrypt" \
    -v "./certs/gateway/letsencrypt/lib:/var/lib/letsencrypt" \
    -p 80:80 -p 443:443 \
    certbot/certbot certonly -d old-bento.example.com -d portal.old-bento.example.com

# Subdomains are optional but recommended, add the ones you want redirected with the '-d' flag
# This creates a single certificate, even if using multiple subdomains.
ls certs/gateway/letsencrypt/live/

# Start the gateway
./bentoctl.bash run gateway
```

If all went well, the `old-bento.example.com` domain should be redirected to `bento.example.com` in a browser.

## Discovery configuration

Bento can serve censored data publicly if configured to do so. This allows anonymous users to take a glimpse into the
data hosted by a Bento node.

When deploying a Bento instance, make sure that the discovery settings are configured properly at the necessary levels.
Consult the [public discovery](./public_discovery.md) documentation for more details.
