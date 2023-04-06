# `bentoV2` Development Repositories Zone

When developing, cloned repositories will be put in this folder and
cloned under their `docker-compose` service name. 

The `docker-compose.dev.yaml` file, in conjunction with the development 
Docker images, will mount this repository as a volume and use it instead of
a production image for the service in question.
