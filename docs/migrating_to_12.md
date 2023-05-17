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


## 2. Create a new client for any bots if needed 

TODO


## 3. Create portal access permissions in the new Bento authorization service

TODO
