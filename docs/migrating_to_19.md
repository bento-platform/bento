# Migrating to Bento v19

TODO


## 1. If using beacon network, update config

Bento v19 has breaking changes to the beacon network configuration file. If using the network, run this command to overwrite the existing config: 

`./bentoctl.bash init-config beacon-network -f`

and make changes accordingly in the file at `lib/beacon/config/beacon_network_config.json` (you may want to copy your old file first so you can remember the network urls.)
