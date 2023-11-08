# Migrating to Bento v14

Version 14 has **removed all MCODE support.** MCODE-specific properties on Individuals in Katsu have been moved to
`extra_properties`.

Updating to Bento 14 should be as straightforward as:

```bash
git pull
./bentoctl.bash start --pull
```
