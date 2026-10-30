# Migrating to Bento v28

**BREAKING CHANGES:**

* Bento Public now has its own OAuth2 client (`bento_public`) with a client secret, separate from the web/portal client
  (`local_bentov2` by default). Bento Public's `CLIENT_ID` changes accordingly, so sign-in on Bento Public will not work
  until the new client is created and its secret is set.
* The S3 configuration for DRS and Drop-Box has changed: `BENTO_{DRS,DROP_BOX}_S3_ENDPOINT` and
  `BENTO_{DRS,DROP_BOX}_S3_USE_HTTPS` are replaced by a single `BENTO_{DRS,DROP_BOX}_S3_ENDPOINT_URL`. Instances using
  S3 for either service must update their `local.env` (see [step 4](#4-update-the-s3-configuration-for-drs-and-drop-box-if-using-s3)).
* The `init-static` command replaces `init-web` (with the same syntax).


## 1. Pull latest Docker containers and stop Bento

```bash
./bentoctl.bash stop
./bentoctl.bash pull
```


## 2. Initialize static authorization data

First, run the following command:

```bash
./bentoctl.bash init-static authz
```

Then, following the structure set by the 
[Bento Authorization Service](https://github.com/bento-platform/bento_authorization_service), optionally edit 
`lib/authz/static_data.json` (after its creation above) to add static grants/groups.


## 3. Create the Bento Public client with secret

Re-run the `init-auth` subcommand of `bentoctl`:

```bash
./bentoctl.bash init-auth
```

This creates a confidential `bento_public` client in the Bento realm, with standard flow, a redirect URI and web origin on
`BENTOV2_PUBLIC_URL`, refresh tokens and PKCE. It prints the client secret to the console; set it in your `local.env`
file similar to the following:

```
# ...
BENTO_PUBLIC_CLIENT_SECRET=my-public-client-secret-here
# ...
```

The default client ID here is `bento_public`, as set in `./etc/default_config.env`.

**If using an external identity provider**, create an equivalent client by hand (confidential, standard flow enabled,
redirect URI `<BENTOV2_PUBLIC_URL>/*`, web origin `<BENTOV2_PUBLIC_URL>`, PKCE enabled with the `S256` method) and set
`BENTO_PUBLIC_CLIENT_ID` and `BENTO_PUBLIC_CLIENT_SECRET` to match.


## 4. (Optional) Clean up the web client

The existing web client (`BENTOV2_AUTH_CLIENT_ID`) is unchanged for existing instances; it keeps the `BENTOV2_PUBLIC_URL`
redirect URI and web origin it was created with. These are no longer needed. To remove them, edit the client in the
Keycloak admin console or the corresponding IdP admin console. New instances only register the portal's redirect URI and web origin.


## 5. Update the S3 configuration for DRS and Drop-Box (if using S3)

Skip this step if neither DRS nor Drop-Box uses S3, i.e. `BENTO_DRS_S3_BUCKET` and `BENTO_DROP_BOX_S3_BUCKET` are
empty or unset.

DRS and Drop-Box now take their S3 endpoint as a single URL, including the protocol. In your `local.env`, replace each
service's `S3_ENDPOINT` and `S3_USE_HTTPS` variables with `S3_ENDPOINT_URL`:

```bash
# Before
BENTO_DRS_S3_ENDPOINT="garage.bentov2.local"
BENTO_DRS_S3_USE_HTTPS=true

# After
BENTO_DRS_S3_ENDPOINT_URL="https://garage.bentov2.local"
```

Do the same for Drop-Box (`BENTO_DROP_BOX_S3_ENDPOINT` and `BENTO_DROP_BOX_S3_USE_HTTPS` become
`BENTO_DROP_BOX_S3_ENDPOINT_URL`). Use `http://` if the endpoint does not use HTTPS. If the endpoint URL is missing, the
services will try to reach AWS S3 instead of your S3 provider.

The other S3 variables (`_S3_BUCKET`, `_S3_ACCESS_KEY`, `_S3_SECRET_KEY`, `_S3_REGION_NAME` and `_VALIDATE_SSL`) keep
their names. Two behaviours have changed:

* The S3 backend is now turned on by setting `BENTO_{DRS,DROP_BOX}_S3_BUCKET` instead of the endpoint. Leave the bucket
  empty to use local storage.
* DRS used to skip TLS certificate verification for S3, whatever `BENTO_DRS_VALIDATE_SSL` was set to. It now follows
  this setting, so if your S3 endpoint uses a self-signed certificate, set `BENTO_DRS_VALIDATE_SSL=false`.

See [Object Storage in Bento](./object_storage.md) for the full list of S3 variables.


## 6. Add 'apply for access' URL to `local.env` (for PCGL instance or developers)

If you want 'apply for access' buttons to show up in the data catalogue / provenance modal, you will need to set the
`BENTO_PUBLIC_APPLY_FOR_ACCESS_URL` environment variable in your `local.env`.


## 7. Restart Bento

```bash
./bentoctl.bash start
```
