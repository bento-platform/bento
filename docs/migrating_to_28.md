# Migrating to Bento v28

**BREAKING CHANGES:**

* Bento Public now has its own OAuth2 client (`bento_public`) with a client secret, separate from the web/portal client
  (`local_bentov2` by default). Bento Public's `CLIENT_ID` changes accordingly, so sign-in on Bento Public will not work
  until the new client is created and its secret is set.
* The `init-static` command replaces `init-web` (with the same syntax).


## 1. Pull latest Docker containers and stop Bento

```bash
./bentoctl.bash stop
./bentoctl.bash pull
```


## 2. Create the Bento Public client with secret

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


## 3. (Optional) Clean up the web client

The existing web client (`BENTOV2_AUTH_CLIENT_ID`) is unchanged for existing instances; it keeps the `BENTOV2_PUBLIC_URL`
redirect URI and web origin it was created with. These are no longer needed. To remove them, edit the client in the
Keycloak admin console or the corresponding IdP admin console. New instances only register the portal's redirect URI and web origin.


## 4. Add 'apply for access' URL to `local.env` (for PCGL instance or developers)

If you want 'apply for access' buttons to show up in the data catalogue / provenance modal, you will need to set the
`BENTO_PUBLIC_APPLY_FOR_ACCESS_URL` environment variable in your `local.env`.


## 5. Restart Bento

```bash
./bentoctl.bash start
```
