# Migrating to Bento v19

## Bento public authorization

Starting with v19, Bento can be configured to only show the data catalogue to authorized users.

Follow the steps in this section to make the data catalogue of an instance private.

First turn on the feature flag in your `local.env`:

```bash
# local.env
BENTO_KATSU_PROJECTS_LIST_AUTHZ=true
```

Then, you must create authorization grants that give the `view:project` permission to the users.
This can be done in the "access management" section of the private portal, or directly in the `authz` service using 
its CLI:

```bash
# In bento dir
./bentoctl.bash shell authz

# In authz shell
# Create grant for users
bento_authz create grant \
  '{"iss": "<ISSUER_HERE>", "sub": <USER_UUID_HERE>}' \
  '{"everything": true}' \
  'view:project'
```

Keep in mind that the `view:project` permission needs to be given to the users of the private portal as well, since 
Katsu performs the authorization checks for all its clients.
Otherwise, private portal users will not be able to use the data manager.

If a user only has the `view:project` permission, they will be able to see the data catalogue, but they need additional 
read permissions to use the search and beacon sections:

```bash
# In authz shell
bento_authz create grant \
  '{"iss": "<ISSUER_HERE>", "sub": <USER_UUID_HERE>}' \
  '{"everything": true}' \
  'query:project_level_boolean' 'query:project_level_counts' 'query:data'
```

For users that will only interact with bento-public, the permissions can be bundled in a single grant.
