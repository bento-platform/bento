# Makefile for BentoV2
include .env



# Run
run-dev:
	docker-compose up -d

run-dev-ingress:
	docker-compose up -d ingress

run-dev-auth:
	docker-compose up -d auth

run-dev-web:
	docker-compose up -d web

run-dev-katsu:
	docker-compose up -d katsu



# Build
build-dev-ingress:
	docker-compose build ingress

# build-dev-auth:
# 	docker-compose build auth

build-dev-web:
	docker-compose build web
	
build-dev-katsu:
	docker-compose build katsu



# Clean up
clean-dev: clean-dev-ingress clean-dev-web clean-dev-katsu

clean-dev-ingress:
	docker rm bentov2-ingress --force; \
	docker rmi bentov2-ingress:0.0.1 --force;

clean-dev-auth:
	docker rm bentov2-auth --force; 

clean-dev-web:
	docker rm bentov2-web --force; \
	docker rmi bentov2-web:0.0.1 --force;

clean-dev-katsu:
	docker rm bentov2-katsu --force; \
	docker rmi bentov2-katsu:0.0.1 --force;




#>>>
# create non-repo directories
# make mkdir

#<<<
.PHONY: mkdir
mkdir:
	mkdir -p $(PWD)/tmp/secrets
	touch  $(PWD)/tmp/secrets/metadata-db-user
	touch  $(PWD)/tmp/secrets/metadata-app-secret
	touch  $(PWD)/tmp/secrets/metadata-db-secret

#>>>
# create secrets for CanDIG services
# make docker-secrets

#<<<
.PHONY: docker-secrets
dev-docker-secrets: 
	@echo admin > $(PWD)/tmp/secrets/metadata-db-user
	@echo dev-app > $(PWD)/tmp/secrets/metadata-app-secret
	@echo devpassword123 > $(PWD)/tmp/secrets/metadata-db-secret



#>>>
# create docker swarm compatbile secrets
# make swarm-secrets

#<<<
.PHONY: swarm-secrets
swarm-secrets:
	docker secret create metadata-app-secret $(PWD)/tmp/secrets/metadata-app-secret
	docker secret create metadata-db-user $(PWD)/tmp/secrets/metadata-db-user
	docker secret create metadata-db-secret $(PWD)/tmp/secrets/metadata-db-secret


#<<<
.PHONY: clean-dev-secrets
clean-dev-secrets:
	rm -rf $(PWD)/tmp/secrets

#>>>
# remove all stacks
# make clean-stack


