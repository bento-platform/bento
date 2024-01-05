# Converting Phenopackets from V1 to V2 using `bentoctl`

Phenopackets JSON documents can be converted from [V1](https://phenopacket-schema.readthedocs.io/en/1.0.0/toplevel.html) 
to [V2](https://phenopacket-schema.readthedocs.io/en/2.0.0/toplevel.html) using `bentoctl` and 
[Phenopacket-tools](https://github.com/phenopackets/phenopacket-tools) as its backend.

For the `bentoctl convert-pheno` command to work, you need to:
1. [Download](http://phenopackets.org/phenopacket-tools/stable/tutorial.html#download-phenopacket-tools) a Phenopacket-tools release.
2. Unzip its content and place the .jar file somwhere safe.
3. Specify the .jar path in `local.env` with the `PHENOTOOL_JAR_PATH` variable

You can then convert a file with:
```shell
bentoctl convert-pheno <source> <target>
```

If the `target` argument is not provided, `bentoctl` will append "_pheno_v2" to the source file's name and save it in its 
parent directory.
