# Migrating to Bento v19

In version 19 of Bento, we've made several improvements to the public researcher portal, as well as adding S3 support
for our Drop Box and Data Repository (DRS) services (which requires a few changes to permissions). We've also made 
**one breaking change** to our Experiment model (specifically, the Instrument sub-model). See the below sections for 
details on how to migrate to version 19.


## Update experiment instruments (if needed)

TODO


## Initialize custom favicon

Bento v19 adds support for custom favicons. Even without a custom favicon, you **MUST** run the following to initialize 
the file mount:

```bash
./bentoctl.bash init-web public
```


## New permissions for WES

Starting with v19, WES interacts with Drop Box and DRS through the network only, rather than with volumes.
This means that WES needs to be authorized to download data from Drop Box:

```bash
# Open a shell in the authz service:
./bentoctl.bash shell authz

# Inside the authz service, find the grants assigned to WES:
bento_authz list grants | grep wes

# In the above list, find the WES grant which has "ingest:data", "ingest:reference_material", etc., and copy the ID.

# Add the "view:drop_box" permission to this grant:
bento_authz add-grant-permissions <GRANT ID> "view:drop_box"
```

Once the permission is added, WES can be used right away, no restarts required.


## Update discovery configurations (preparing for future deprecations)

Katsu has been reconfigured such that the `mapping_for_search_filter` field is no longer relevant, although it still 
works for overriding `mapping`. Instead, we can predictably re-map `mapping` from the perspective of 
`phenopacket`/`individual`, which is in all cases what this field was being used for.

Thus, unless there exists some edge case that must be fixed in a future version that we do not know about yet, these 
`mapping_for_search_filter` properties should be removed from the config.


## If using a beacon network, update config

Bento v19 has breaking changes to the beacon network configuration file. If using the network, run this command to 
overwrite the existing config: 

`./bentoctl.bash init-config beacon-network -f`

and make changes accordingly in the file at `lib/beacon/config/beacon_network_config.json` (you may want to copy your 
old file first so you can remember the network URLs.)
