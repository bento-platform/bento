# Makefile for BentoV2

include .env

run-dev:
	docker-compose up -d

run-dev-ingress:
	docker-compose up -d ingress

run-dev-web:
	docker-compose up -d web

run-dev-katsu:
	docker-compose up -d katsu


build-dev-ingress:
	docker-compose build ingress

build-dev-web:
	docker-compose build web
	
build-dev-katsu:
	docker-compose build katsu






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


