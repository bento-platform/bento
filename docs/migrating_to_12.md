# Migrating to Bento v12

The following is a migration guide for going from Bento v2.11 to Bento v12.

Note the change in versioning scheme for this release; we dropped the `2.` prefix.


## 1. Convert the Keycloak client to be `public` and enable PKCE

To do this, sign in to Keycloak as an administrator and navigate to the realm & Bento client.
Then, turn off "Client authentication" and make sure the settings are as follows, with only
"Standard flow" enabled and **save your changes.**

<img src="img/client_setup_v12.png" width="500" height="214" alt="Client configuration for Bento Keycloak for v12" />

Then, enable PKCE by going to the "Advanced" tab, scrolling down to "Advanced settings", and setting the
`Proof Key for Code Exchange Code Challenge Method` setting to `S256`. Finally, **save your changes** again.


## 2. Create a new client for any bots (*if needed*) 

In Keycloak, create separate clients for any bots. These should have "Client authentication" **ON**.

For the legacy bot authentication method, "Direct access grants" will need to be **ON** as well.

For a more modern bot approach, turn "Direct access grants" **OFF** and turn "Service account roles" **ON**,
thereby enabling the "Client credentials" authentication flow.


## 3. Create superuser permissions in the new Bento authorization service

First, open a shell in the authorization service container:

```bash
./bentoctl.bash shell authz
```

Then, run the following command for each user ID you wish to assign superuser permissions to:

```bash
bento_authz assign-all-to-user iss sub
```

Where `iss` is the issuer (for example, `https://bentov2auth.local/realms/bentov2`) and `sub` is the subject ID,
which in Keycloak should be a UUID.


## 4. Create bot permissions in the new Bento authorization service (*if needed*)

TODO
