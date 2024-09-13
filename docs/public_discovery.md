# Public data discovery configuration

New in Bento v17.

Previously, the public data configuration given to Katsu was applied on all the metadata contained in the service.
This configuration declares which fields can be queried publicly for discovery purposes, which charts to display
and which censorship rules to apply on the results.

Katsu can hold multiple projects/datasets that may use different fields, require specific charts or custom
`extra_properties` schemas at the project level.
Therefore, there is a need to tailor the discovery configuration at different levels.

Bento v17 gives the ability to specify a scoped Discovery configuration at the following levels:
-   Dataset
    -   Optional at dataset creation
    -   For scoped queries on public endpoints targeting a project and dataset:
        -   Katsu will use the dataset's discovery configuration
        -   If no configuration is found, fallsback on the parent project's discovery
-   Project
    -   Optional at project creation
    -   For scoped queries on public endpoints targeting a project only:
        -   Katsu will use the project's discovery configuration
        -   If no configuration is found, fallsback on the node's config
-   Node
    -   Optional during Katsu deployment
    -   Uses the legacy `lib/katsu/config.json` file mount
    -   For non-scoped queries on public endpoints:
        -   Katsu will use the node's discovery, if there is one.
        -   If no node configuration is found, Katsu will respond with a 404 status.
    -   For scoped queries on public endpoints:
        -   Katsu will fallback on the node's discovery if the project and/or dataset in the scope don't have one
        -   If no node configuration is found, Katsu will respond with a 404 status.

In previous versions of Bento, the bento_public web application could only show the aggregated data of all projects and datasets.
Now, bento_public users can select a project/dataset scope in order to only retrieve the data contained in it.

Given that projects/datasets use different fields or may have custom extra properties, depending on the study, you can now
declare the fields and charts of interest at the relevant level.
