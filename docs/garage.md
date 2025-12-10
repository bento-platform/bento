# Using Garage Object Storage in Bento

This document covers how to use [Garage](https://garagehq.deuxfleurs.fr/), a lightweight, self-hosted, S3-compatible object storage solution, which replaces MinIO in your Bento deployment.

## Architecture

Garage exposes three ports for different purposes:

| Port     | Purpose        | Used By                              | Protocol                  |
| -------- | -------------- | ------------------------------------ | ------------------------- |
| **3900** | S3 API         | Services (DRS, Drop-Box)             | HTTP REST (S3-compatible) |
| **3901** | RPC (Internal) | Garage nodes (cluster communication) | Custom RPC                |
| **3903** | Admin API      | Administration and management        | HTTP REST                 |

In Bento's single-node configuration (`replication_mode = "1"`), the RPC port is still required for internal operations.

## Quick Start

### 1. Initialize Docker Networks, Directories and Certs

```bash
./bentoctl.bash init-docker
./bentoctl.bash init-dirs
./bentoctl.bash init-certs  # use -f flag if certs directory already exists
./bentoctl.bash restart gateway
```

This creates the required `bentov2-garage-net` network.

> **Note**: If you see "all predefined address pools have been fully subnetted", run `docker network prune -f` to clean up unused networks, then retry.

### 2. Add Garage Domain to /etc/hosts

Add the following entry to your `/etc/hosts` file for local access:

```bash
127.0.0.1  garage.bentov2.local
127.0.0.1  admin.garage.bentov2.local
```

### 3. Configure Garage Variables

Edit your `local.env` file and set the following variables:

```bash
# local.env

# Enable Garage profile
BENTO_GARAGE_ENABLED='true'

# Generate RPC secret (must be exactly 64 hexadecimal characters)
# Use: openssl rand -hex 32
BENTO_GARAGE_RPC_SECRET='<your-64-char-hex-secret>'

# Set admin token (use a secure value for production)
BENTO_GARAGE_ADMIN_TOKEN='<your-secure-admin-token>'
```

**Generate the RPC secret:**

```bash
openssl rand -hex 32
```

> ⚠️ **Important**:
> - The RPC secret must be exactly 64 hexadecimal characters (32 bytes)
> - For development, you can use the default value from `etc/bento_dev.env`
> - For production, always generate new secrets and never commit them to git

### 4. Initialize Garage

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

**IMPORTANT:** Save the Access Key and Secret Key printed by this command - you'll need them in the next step.

> **Note**: You don't need to manually run `./bentoctl.bash run garage` - the init command will start the container automatically if it's not running.

### 5. Configure Drop Box Service

Add the following Drop Box configuration to your `local.env` file:

```bash
# local.env

# Drop Box S3 Configuration
BENTO_DROP_BOX_S3_ENDPOINT="garage.bentov2.local"       # Access via gateway
BENTO_DROP_BOX_S3_USE_HTTPS=true                        # HTTPS through gateway
BENTO_DROP_BOX_S3_BUCKET="drop-box"                     # Created by init-garage
BENTO_DROP_BOX_S3_REGION_NAME="garage"                  # Must match garage.toml
BENTO_DROP_BOX_S3_ACCESS_KEY="<from-init-garage>"       # Save from init-garage output
BENTO_DROP_BOX_S3_SECRET_KEY="<from-init-garage>"       # Save from init-garage output
BENTO_DROP_BOX_VALIDATE_SSL=false                       # Set to false for self-signed certs
```

Restart Drop Box:

```bash
./bentoctl.bash restart drop-box
```

### 6. Configure DRS Service

Add the following DRS configuration to your `local.env` file:

```bash
# local.env

# DRS S3 Configuration
BENTO_DRS_S3_ENDPOINT="garage.bentov2.local"            # Access via gateway
BENTO_DRS_S3_USE_HTTPS=true                             # HTTPS through gateway
BENTO_DRS_S3_BUCKET="drs"                               # Created by init-garage
BENTO_DRS_S3_REGION_NAME="garage"                       # Must match garage.toml
BENTO_DRS_S3_ACCESS_KEY="<from-init-garage>"            # Save from init-garage output
BENTO_DRS_S3_SECRET_KEY="<from-init-garage>"            # Save from init-garage output
BENTO_DRS_VALIDATE_SSL=false                            # Set to false for self-signed certs
```

Restart DRS:

```bash
./bentoctl.bash restart drs
```

## Configuration Reference
### Domain Configuration

```bash
# Domain for accessing Garage S3 API through the gateway
BENTO_GARAGE_DOMAIN=garage.${BENTOV2_DOMAIN}
```

This domain is used for:

- **S3 API access**: `https://garage.bentov2.local/bucket/object` (path-style)

### Security Configuration

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

[admin]
api_bind_addr = "[::]:3903"
admin_token = "<from BENTO_GARAGE_ADMIN_TOKEN>"
```

All bucket access uses path-style addressing: `https://garage.bentov2.local/bucket/object`

### Docker Compose Configuration

The Garage service is configured in `lib/garage/docker-compose.garage.yaml`:

**Key configuration:**

- Admin port (3903) is published to localhost for initialization
- No healthcheck (Garage image doesn't include curl)
- Other ports (3900-3901) are exposed only to internal network
- Config file mounted read-only at `/etc/garage.toml`

**Port configuration:**

```yaml
ports:
  - "3903:3903" # Admin API published for init script
  - "3900:3900" # S3 API 
expose:
  - 3901 # RPC (internal network only)
```

> **Note**: The admin port must be published to localhost because the `init-garage` script runs on the host and needs to make API calls to configure the cluster.

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

## Resources

- [Garage Documentation](https://garagehq.deuxfleurs.fr/documentation/)
- [Garage Admin API Reference](https://garagehq.deuxfleurs.fr/documentation/reference-manual/admin-api/)
- [S3 Compatibility](https://garagehq.deuxfleurs.fr/documentation/reference-manual/s3-compatibility/)
- [Bento Object Storage Guide](object_storage.md)
