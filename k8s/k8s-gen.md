# Bento Kubernetes resources

Currently, Bento uses Docker Compose for development and deployment.

Kubernetes (k8s) is a container orchestration system, which enables better deployment automation and scaling.

As we are porting Bento for k8s, our goal is **NOT** to completely replace Docker Compose with k8s resources.

Compose is already tightly integrated with `bentoctl`, and it offers us a simple and reliable development environment.

The goal of this work is to keep using Docker Compose as the source of truth for defining a Bento stack, and to have a mechanism 
that allows us to translate Docker Compose stacks into k8s resources for production deployments.

To achieve this, we will be using the [Kompose](https://kompose.io/) CLI tool, which is officialy supported and developed
by the Kubernetes project for this use-case.

## Converting Bento Compose files to Kubernets

WIP: simple proof of concept usage of Kompose for Bento

```bash
# Generate a resolved Docker Compose config file with bentoctl
./bentoctl.bash compose-config >> k8s/resolved-compose.yaml

# Convert the compose config to k8s resources using Kompose
mkdir k8s/kompose
kompose -f k8s/resolved-compose.yaml convert -o k8s/kompose

# Deploy the resources to a k8s cluster
kubectl apply -f k8s/kompose
```

## Kompose labels

Per Kompose's docs on [labels](https://kompose.io/user-guide/#labels):
> `kompose` supports Kompose-specific labels within the `compose.yaml` file to get you the rest of the way there.
> 
> Labels are an important kompose concept as they allow you to add Kubernetes modifications without having to edit the YAML afterwards.
> 
> For example, adding an init container, or a custom readiness check.

To bridge the gap between k8s and Docker Kompose, we will need to include various Kompose labels in our compose files.

These labels will only take effect when converting using Kompose.

