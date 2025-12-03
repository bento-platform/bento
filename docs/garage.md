# Using Garage Object Storage in Bento

This document covers how to use [Garage](https://garagehq.deuxfleurs.fr/), a lightweight, self-hosted, S3-compatible object storage solution, as an alternative to MinIO in your Bento deployment.

## Architecture

Garage exposes four ports for different purposes:

| Port     | Purpose        | Used By                              | Protocol                  |
| -------- | -------------- | ------------------------------------ | ------------------------- |
| **3900** | S3 API         | Services (DRS, Drop-Box)             | HTTP REST (S3-compatible) |
| **3901** | RPC (Internal) | Garage nodes (cluster communication) | Custom RPC                |
| **3902** | Web Server     | Static website hosting               | HTTP                      |
| **3903** | Admin API      | Administration and management        | HTTP REST                 |

In Bento's single-node configuration (`replication_mode = "1"`), the RPC port is still required for internal operations.

### Port Configuration

- **Ports 3900-3902** (S3 API, RPC, Web): Exposed to internal Docker network only
  - Services access these via container name: `http://bentov2-garage:3900`
- **Port 3903** (Admin API): Published to localhost
  - Required for `init-garage` script to configure the cluster
  - Accessible at: `http://localhost:3903`

## Prerequisites

Before setting up Garage, ensure you have:

1. **Docker networks created**: Run `./bentoctl.bash init-docker` first

   - This creates the required `bentov2-garage-net` network
   - If you see "all predefined address pools have been fully subnetted", run `docker network prune -f` to clean up unused networks, then retry

2. **Valid RPC secret**: Must be exactly 64 hexadecimal characters (32 bytes)
   - For development: The default in `etc/bento_dev.env` is valid
   - For production: Generate with `openssl rand -hex 32` and set in `local.env`

## Quick Start

### 0. Run Prerequisites

Ensure Docker networks exist:

```bash
./bentoctl.bash init-docker
```

### 1. Enable Garage Profile

Garage is deployed as a Docker Compose profile. To enable it, add `garage` to your enabled profiles in `local.env`:

```bash
# local.env
BENTO_GARAGE_ENABLED='true'
```

### 2. Generate SSL Certificates (HTTPS Access)

For HTTPS access to `garage.bentov2.local`, you need SSL certificates. You have two options:

**Option A: Use existing Bento certificates (temporary/development)**

The garage nginx configuration currently uses the main Bento certificate. This will cause certificate warnings in browsers but will work with `-k` flag in curl.

**Option B: Generate dedicated certificates for Garage**

```bash
# Generate self-signed certificate for garage domain
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout ./local/certs/gateway/garage_privkey1.key \
  -out ./local/certs/gateway/garage_fullchain1.crt \
  -days 365 -subj "/CN=garage.bentov2.local" \
  -addext "subjectAltName=DNS:garage.bentov2.local,DNS:*.s3.garage.bentov2.local,DNS:*.web.garage.bentov2.local"

# Update gateway configuration to use dedicated cert
# Edit lib/gateway/public_services/garage.conf.tpl to use:
# ssl_certificate ${BENTO_GATEWAY_INTERNAL_GARAGE_FULLCHAIN_RELATIVE_PATH};
# ssl_certificate_key ${BENTO_GATEWAY_INTERNAL_GARAGE_PRIVKEY_RELATIVE_PATH};

# Restart gateway to apply new configuration
./bentoctl.bash restart gateway
```

> **Note**:
> - For production, use proper certificates from Let's Encrypt or your certificate authority
> - Gateway restart is required for the garage nginx configuration to be rendered from template
> - The garage.conf.tpl template is processed at gateway startup

### 3. Initialize Garage

Initialize the Garage cluster with single-node layout and create default buckets:

```bash
./bentoctl.bash init-garage
```

This command will:

1. Validate the RPC secret format (64 hex characters)
2. Check if the Garage container is running (starts it if needed)
3. Generate the `garage.toml` configuration file
4. Wait for the Admin API to be ready (polls http://localhost:3903)
5. Configure a single-node cluster layout
6. Create S3 access credentials
7. Create default buckets: `drs` and `drop-box`
8. Grant bucket permissions to the access key

**IMPORTANT:** Save the Access Key and Secret Key printed by this command - you'll need them to configure Bento services.

> **Note**: You don't need to manually run `./bentoctl.bash run garage` - the init command will start the container automatically if it's not running.

## Configuration

### Environment Variables

Garage configuration follows Bento's standard configuration hierarchy:

1. **`etc/default_config.env`** - Base defaults (empty values)
2. **`etc/bento.env`** - Core configuration (image, ports, paths)
3. **`etc/bento_dev.env`** or **`etc/bento_deploy.env`** - Environment-specific defaults
4. **`local.env`** - Your local overrides (not in git)

#### Core Configuration (from bento.env)

```bash
# Core configuration (bento.env)
BENTO_GARAGE_IMAGE=dxflrs/garage
BENTO_GARAGE_IMAGE_VERSION=v1.0.1
BENTO_GARAGE_CONTAINER_NAME=${BENTOV2_PREFIX}-garage
BENTO_GARAGE_CONFIG_DIR=${PWD}/lib/garage/config
BENTO_GARAGE_META_DIR=${BENTO_FAST_DATA_DIR}/garage/meta
BENTO_GARAGE_DATA_DIR=${BENTO_SLOW_DATA_DIR}/garage/data
BENTO_GARAGE_NETWORK=${BENTOV2_PREFIX}-garage-net

# Port assignments
BENTO_GARAGE_S3_API_PORT=3900
BENTO_GARAGE_RPC_PORT=3901
BENTO_GARAGE_WEB_PORT=3902
BENTO_GARAGE_ADMIN_PORT=3903

```

#### Domain Configuration

```bash
# Domain for accessing Garage S3 API through the gateway
BENTO_GARAGE_DOMAIN=garage.${BENTOV2_DOMAIN}
```

This domain is used for:
- **S3 API access**: `https://garage.bentov2.local` (path-style: `/bucket/object`)
- **Virtual-hosted buckets**: `https://bucket.s3.garage.bentov2.local/object` (optional)
- **Web interface**: `https://bucket.web.garage.bentov2.local` (optional)

> **Note**: For local development, add these entries to your `/etc/hosts` file:
> ```bash
> # Main S3 API endpoint
> 127.0.0.1  garage.bentov2.local
>
> # Example virtual-hosted bucket subdomains (add as needed)
> 127.0.0.1  drs.s3.garage.bentov2.local
> 127.0.0.1  drop-box.s3.garage.bentov2.local
>
> # Example web interface subdomains (add as needed)
> 127.0.0.1  drs.web.garage.bentov2.local
> 127.0.0.1  drop-box.web.garage.bentov2.local
> ```
>
> **Note**: Wildcard DNS (e.g., `*.s3.garage.bentov2.local`) is not supported in `/etc/hosts`. You need to add each subdomain individually as you create buckets.

#### Security Configuration

**For Development** (from `etc/bento_dev.env`):

```bash
# IMPORTANT: RPC secret must be exactly 64 hexadecimal characters (32 bytes)
# Generate with: openssl rand -hex 32
BENTO_GARAGE_RPC_SECRET=41f2965d423fe5c3904a76f7c7ab4ba186072fb4d7faf28643ddc8aaa3129e13
BENTO_GARAGE_ADMIN_TOKEN=devgarageadmin789
```

**For Production** (set in `local.env` or override in `etc/bento_deploy.env`):

```bash
# Generate with: openssl rand -hex 32
BENTO_GARAGE_RPC_SECRET=<your-generated-64-char-hex-secret>
BENTO_GARAGE_ADMIN_TOKEN=<your-secure-admin-token>
```

> ⚠️ **Important**: The RPC secret must be exactly 64 hexadecimal characters (32 bytes). Generate with `openssl rand -hex 32`.

**Best Practices:**

- **Development**: Use the valid default in `bento_dev.env`
- **Production**: Generate new secrets and set in `local.env` (never commit to git)
- Both secrets should be treated as sensitive credentials

### Garage Configuration File

The `garage.toml` file is automatically generated by `init-garage` from the template at `etc/templates/garage/template.toml`. It substitutes environment variables and stores the result at `lib/garage/config/garage.toml`:

```toml
metadata_dir = "/var/lib/garage/meta"
data_dir = "/var/lib/garage/data"

replication_mode = "1"  # Single node

rpc_bind_addr = "[::]:3901"
rpc_public_addr = "127.0.0.1:3901"
rpc_secret = "<from BENTO_GARAGE_RPC_SECRET>"

[s3_api]
s3_region = "garage"
api_bind_addr = "[::]:3900"
root_domain = ".s3.<from BENTO_GARAGE_DOMAIN>"  # e.g., .s3.garage.bentov2.local

[s3_web]
bind_addr = "[::]:3902"
root_domain = ".web.<from BENTO_GARAGE_DOMAIN>"  # e.g., .web.garage.bentov2.local

[admin]
api_bind_addr = "[::]:3903"
admin_token = "<from BENTO_GARAGE_ADMIN_TOKEN>"
```

**What the domains mean:**
- `root_domain` in `[s3_api]`: Enables virtual-hosted-style bucket access (e.g., `https://mybucket.s3.garage.bentov2.local/object`)
- `root_domain` in `[s3_web]`: Enables web interface for buckets (e.g., `https://mybucket.web.garage.bentov2.local`)
- Both use the `BENTO_GARAGE_DOMAIN` environment variable (defaults to `garage.bentov2.local`)

> **Note**: These are optional features. Standard path-style access (`https://garage.bentov2.local/mybucket/object`) works without them.

### Docker Compose Configuration

The Garage service is configured in `lib/garage/docker-compose.garage.yaml`:

**Key configuration:**

- Admin port (3903) is published to localhost for initialization
- No healthcheck (Garage image doesn't include curl)
- Other ports (3900-3902) are exposed only to internal network
- Config file mounted read-only at `/etc/garage.toml`

**Port configuration:**

```yaml
ports:
  - "3903:3903" # Admin API published for init script
expose:
  - 3900 # S3 API (internal network only)
  - 3901 # RPC (internal network only)
  - 3902 # Web (internal network only)
```

> **Note**: The admin port must be published to localhost because the `init-garage` script runs on the host and needs to make API calls to configure the cluster.

## Configuring Bento Services

After initializing Garage, configure your Bento services to use it for object storage.

### Drop Box

Edit your `local.env` file:

```bash
# local.env

# Use the container name as the endpoint (no protocol)
BENTO_DROP_BOX_S3_ENDPOINT="${BENTO_GARAGE_CONTAINER_NAME}"
BENTO_DROP_BOX_S3_USE_HTTPS=false                       # HTTP within Docker network
BENTO_DROP_BOX_S3_BUCKET="drop-box"                     # Created by init-garage
BENTO_DROP_BOX_S3_REGION_NAME="garage"                  # Must match garage.toml
BENTO_DROP_BOX_S3_ACCESS_KEY="<from init-garage>"       # Save from init-garage output
BENTO_DROP_BOX_S3_SECRET_KEY="<from init-garage>"       # Save from init-garage output
BENTO_DROP_BOX_VALIDATE_SSL=false                       # Not using SSL internally
```

Restart Drop Box:

```bash
./bentoctl.bash restart drop-box
```

### DRS

Edit your `local.env` file:

```bash
# local.env

BENTO_DRS_S3_ENDPOINT="${BENTO_GARAGE_CONTAINER_NAME}"  # Use container name
BENTO_DRS_S3_USE_HTTPS=false                            # HTTP within Docker network
BENTO_DRS_S3_BUCKET="drs"                               # Created by init-garage
BENTO_DRS_S3_REGION_NAME="garage"                       # Must match garage.toml
BENTO_DRS_S3_ACCESS_KEY="<from init-garage>"            # Save from init-garage output
BENTO_DRS_S3_SECRET_KEY="<from init-garage>"            # Save from init-garage output
BENTO_DRS_VALIDATE_SSL=false                            # Not using SSL internally
```

Restart DRS:

```bash
./bentoctl.bash restart drs
```

## Verification

### Check Garage Status

View Garage logs:

```bash
./bentoctl.bash logs garage
```

Check if Garage is healthy:

```bash
docker ps | grep garage
```

### Verify S3 Integration

Check if services are using S3:

```bash
# Check DRS logs for S3 activity
./bentoctl.bash logs drs | grep -i s3

# Check Drop-Box logs for S3 activity
./bentoctl.bash logs drop-box | grep -i s3
```

### Using Garage Admin API

You can interact with Garage's Admin API directly:

```bash
# Set admin token
ADMIN_TOKEN="<from BENTO_GARAGE_ADMIN_TOKEN>"

# Get cluster status
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:3903/status

# List buckets
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:3903/bucket

# List keys
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:3903/key
```

## Managing Buckets

### Create Additional Buckets

You can create additional buckets using the Admin API:

```bash
ADMIN_TOKEN="<from BENTO_GARAGE_ADMIN_TOKEN>"
ACCESS_KEY="<from init-garage>"

# Create bucket
curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"globalAlias": "my-new-bucket"}' \
  http://localhost:3903/bucket

# Get bucket ID from response, then grant permissions
BUCKET_ID="<bucket-id-from-response>"

curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"bucketId\": \"$BUCKET_ID\",
    \"accessKeyId\": \"$ACCESS_KEY\",
    \"permissions\": {
      \"read\": true,
      \"write\": true,
      \"owner\": true
    }
  }" \
  http://localhost:3903/bucket/allow
```

### Using S3 CLI Tools

Garage is S3-compatible, so you can use standard S3 tools:

```bash
# Using AWS CLI
aws configure set aws_access_key_id <ACCESS_KEY>
aws configure set aws_secret_access_key <SECRET_KEY>
aws --endpoint-url http://localhost:3900 s3 ls

# Using s3cmd (create ~/.s3cfg first)
s3cmd --host=localhost:3900 --host-bucket=localhost:3900 \
  --no-ssl ls
```

## Data Persistence

Garage stores data in two locations:

- **Metadata**: `${BENTO_FAST_DATA_DIR}/garage/meta` (default: `./data/garage/meta`)
- **Object data**: `${BENTO_SLOW_DATA_DIR}/garage/data` (default: `./data/garage/data`)

These directories are mounted as Docker volumes and persist across container restarts.

## Troubleshooting

### Garage Container Won't Start

Check the logs:

```bash
./bentoctl.bash logs garage
```

Common issues:

- RPC secret or admin token not set
- Config file missing or invalid
- Ports already in use
- Network not created (see below)

### Invalid RPC Secret Error

**Error**: `Invalid RPC secret key: expected 32 bits of entropy`

**Cause**: RPC secret is not exactly 64 hex characters (32 bytes)

**Solution**:

1. Generate valid secret: `openssl rand -hex 32`
2. Update in `etc/bento_dev.env` or `local.env`:
   ```bash
   BENTO_GARAGE_RPC_SECRET=<64-char-hex-string>
   ```
3. Recreate config: `./bentoctl.bash init-garage`
4. Restart container: `./bentoctl.bash restart garage`

### Config File Created as Directory

**Error**: `Is a directory` or mount errors

**Cause**: Docker created `garage.toml` as directory when file didn't exist during mount

**Solution**:

1. Stop container: `./bentoctl.bash stop garage`
2. Remove directory:
   ```bash
   docker run --rm -v "${PWD}/lib/garage/config:/config" alpine rm -rf /config/garage.toml
   ```
3. Run init again: `./bentoctl.bash init-garage`

### Network Not Found

**Error**: `network bentov2-garage-net not found`

**Cause**: Docker network wasn't created

**Solutions**:

1. Run `./bentoctl.bash init-docker`
2. If that fails with "all predefined address pools have been fully subnetted":
   ```bash
   docker network prune -f
   ./bentoctl.bash init-docker
   ```

### Init-Garage Fails

Ensure:

1. Garage container is running: `docker ps | grep garage`
2. Container is healthy (may take 30-60 seconds)
3. Admin token is set in environment variables
4. RPC secret is valid (64 hex characters)

### Services Can't Connect to Garage

Verify:

1. Services are on the same Docker network (`garage-net`)
2. Endpoint uses container name, not `localhost`
3. Port 3900 is accessible within the network
4. Access key and secret are correct

### Permission Denied Errors

Check:

1. Bucket permissions are set correctly
2. Access key has proper permissions for the bucket
3. Region matches (`garage` in this setup)

### Admin API Connection Refused

**Error**: `Connection refused` when running `init-garage`

**Cause**: Admin port not accessible on localhost

**Solutions**:

1. Verify port is published in docker-compose:

   ```bash
   docker ps --filter "name=garage" --format "table {{.Names}}\t{{.Ports}}"
   ```

   Should show: `0.0.0.0:3903->3903/tcp`

2. Check if port 3903 is in use by another process:

   ```bash
   sudo lsof -i :3903
   ```

3. Restart container to apply port changes:
   ```bash
   ./bentoctl.bash restart garage
   ```

### Container Shows Unhealthy (Older Versions)

**Error**: Container status shows "unhealthy"

**Cause**: Older docker-compose configuration included healthcheck using `curl`, which is not available in Garage image

**Solution**: This has been fixed in the current configuration. If you see this:

1. Update your `lib/garage/docker-compose.garage.yaml` from the latest version
2. Restart container: `./bentoctl.bash restart garage`

**Note**: The healthcheck has been removed as it's not needed - the `init-garage` script directly checks if the Admin API is responsive.

### Admin API Version Compatibility

**Note**: Bento uses Garage Admin API v1 (`/v1/` endpoints). The older v0 API has been deprecated in Garage v1.0+.

If you're writing custom scripts or tools, ensure you use the v1 API endpoints:
- `/v1/status` - Cluster status
- `/v1/layout` - Layout configuration
- `/v1/key` - Key management
- `/v1/bucket` - Bucket management
- `/health` - Health check (no version prefix, no auth required)

## Testing Garage Access

After setting up Garage and restarting the gateway, test access:

```bash
# Test Admin API (direct access, no gateway)
curl http://localhost:3903/health

# Test S3 API through gateway (HTTP - will redirect to HTTPS)
curl http://garage.bentov2.local/

# Test S3 API through gateway (HTTPS - requires valid certificate or -k flag)
curl -k https://garage.bentov2.local/

# List buckets using AWS CLI
aws --endpoint-url https://garage.bentov2.local \
    --no-verify-ssl \
    s3 ls

# Upload a test file
echo "test" > test.txt
aws --endpoint-url https://garage.bentov2.local \
    --no-verify-ssl \
    s3 cp test.txt s3://drs/test.txt
```

> **Note**: Use `--no-verify-ssl` with AWS CLI when using self-signed certificates.

## Using the Web Interface

Garage supports serving static websites directly from buckets using the web interface feature.

### Setup Web Hosting for a Bucket

1. **Upload website files** to your bucket (e.g., `index.html`, `error.html`)

2. **Configure the bucket for web hosting** using the Admin API:

```bash
# Get your bucket ID
curl -H "Authorization: Bearer devgarageadmin789" http://localhost:3903/v1/bucket | jq '.[] | select(.globalAliases[] == "mybucket")'

# Enable website for the bucket
curl -X PUT -H "Authorization: Bearer devgarageadmin789" \
  -H "Content-Type: application/json" \
  -d '{"indexDocument": "index.html", "errorDocument": "error.html"}' \
  http://localhost:3903/v1/bucket/<bucket-id>/website
```

3. **Add subdomain to `/etc/hosts`**:

```bash
127.0.0.1  mybucket.web.garage.bentov2.local
```

4. **Access your website** at: `https://mybucket.web.garage.bentov2.local`

### Example: Hosting Documentation

```bash
# Create a bucket for docs
curl -X POST -H "Authorization: Bearer devgarageadmin789" \
  -H "Content-Type: application/json" \
  -d '{"globalAlias": "docs"}' \
  http://localhost:3903/v1/bucket

# Upload HTML files using AWS CLI
aws --endpoint-url https://garage.bentov2.local s3 cp ./index.html s3://docs/
aws --endpoint-url https://garage.bentov2.local s3 cp ./404.html s3://docs/

# Enable web hosting
curl -X PUT -H "Authorization: Bearer devgarageadmin789" \
  -H "Content-Type: application/json" \
  -d '{"indexDocument": "index.html", "errorDocument": "404.html"}' \
  http://localhost:3903/v1/bucket/<bucket-id>/website

# Add to /etc/hosts
echo "127.0.0.1  docs.web.garage.bentov2.local" | sudo tee -a /etc/hosts

# Visit https://docs.web.garage.bentov2.local
```

## Migrating from MinIO to Garage

If you're migrating from MinIO to Garage:

1. **Export data from MinIO** using `mc mirror` or similar tools
2. **Initialize Garage** with `./bentoctl.bash init-garage`
3. **Upload data to Garage** using S3 CLI tools (see above)
4. **Update service configuration** to point to Garage
5. **Restart services** to apply changes

See [object_storage.md](object_storage.md) for more details on data migration.

## Production Considerations

For production deployments:

1. **Security**

   - Use strong random values for `BENTO_GARAGE_RPC_SECRET` and `BENTO_GARAGE_ADMIN_TOKEN`
   - Store secrets in `local.env` (not committed to git)
   - Consider enabling HTTPS for external access
   - Restrict Admin API access

2. **Performance**

   - Place metadata on fast storage (SSD)
   - Place object data on slower, larger storage (HDD/object storage)
   - Adjust capacity in layout configuration based on actual storage

3. **Backups**

   - Backup both metadata and data directories regularly
   - Consider Garage's built-in replication for redundancy

4. **Monitoring**
   - Monitor Garage logs for errors
   - Check storage capacity regularly
   - Monitor API response times

## Resources

- [Garage Documentation](https://garagehq.deuxfleurs.fr/documentation/)
- [Garage Admin API Reference](https://garagehq.deuxfleurs.fr/documentation/reference-manual/admin-api/)
- [S3 Compatibility](https://garagehq.deuxfleurs.fr/documentation/reference-manual/s3-compatibility/)
- [Bento Object Storage Guide](object_storage.md)
