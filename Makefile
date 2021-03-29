# Makefile for BentoV2

# import global variables
env ?= .env

include $(env)
export $(shell sed 's/=.*//' $(env))



# Local directories
data-dirs:
	mkdir -p ${BENTOV2_AUTH_VOL_DIR}
	mkdir -p ${BENTOV2_KATSU_DB_VOL_DIR}
	mkdir -p ${BENTOV2_NOTIFICATION_VOL_DIR}
	mkdir -p ${BENTOV2_FEDERATION_VOL_DIR}
	mkdir -p ${BENTOV2_WES_VOL_DIR}
	mkdir -p ${BENTOV2_REDIS_VOL_DIR}


#>>>
# init chord services

#<<<
.PHONY: init-chord-services
init-chord-services:

	# copy instance_config to gateway	
	envsubst < ${PWD}/etc/templates/instance_config.example.json > $(PWD)/lib/gateway/instance_config.json;

	# copy services json to the microservices that need it
	cp $(PWD)/etc/templates/chord_services.example.json $(PWD)/lib/logging/chord_services.json;
	cp $(PWD)/etc/templates/chord_services.example.json $(PWD)/lib/service-registry/chord_services.json;
	cp $(PWD)/etc/templates/chord_services.example.json $(PWD)/lib/wes/chord_services.json;


# Run
run:
	docker-compose up -d
	# docker-compose -f docker-compose.dev.yaml -f docker-compose.yaml up -d

run-gateway:
	docker-compose up -d gateway

run-auth:
	docker-compose up -d auth

run-drop-box:
	docker-compose up -d drop-box

run-service-registry:
	docker-compose up -d service-registry

run-web: clean-web
	docker-compose up -d web

# For local development
run-web-dev: clean-web
	docker-compose -f docker-compose.dev.yaml -f docker-compose.yaml up -d web
#

run-katsu:
	docker-compose up -d katsu

run-logging:
	docker-compose up -d logging

run-drs:
	docker-compose up -d drs

run-variant:
	docker-compose up -d variant

run-notification:
	docker-compose up -d notification

run-federation:
	docker-compose up -d federation

run-event-relay:
	docker-compose up -d event-relay

run-wes:
	docker-compose up -d wes

run-redis:
	docker-compose up -d redis





# Build
build-common-base:
	docker-compose -f docker-compose.base.yaml build common-alpine-python


build-gateway:
	docker-compose build gateway

# build-auth:
# 	docker-compose build auth

build-drop-box:
	docker-compose build drop-box

build-service-registry:
	docker-compose build service-registry

build-web:
	docker-compose build web
	
build-katsu:
	docker-compose build katsu

build-logging:
	docker-compose build logging

build-drs:
	docker-compose build drs

build-variant:
	docker-compose build variant

build-notification:
	docker-compose build notification

build-federation:
	docker-compose build federation

build-event-relay:
	docker-compose build event-relay

build-wes:
	docker-compose build wes

build-redis:
	docker-compose build redis



stop:
	docker-compose down;



# Clean up
clean-common-base:
	docker rmi bentov2-common-alpine-python:0.0.1 --force;

clean: clean-gateway \
		clean-auth clean-web clean-drop-box clean-drs \
		clean-service-registry clean-katsu clean-drs \
		clean-variant clean-federation clean-wes \
		clean-logging clean-notification clean-event-relay

# TODO: use env variables for container versions
clean-gateway:
	docker-compose stop gateway;
	docker rm bentov2-gateway --force; \
	docker rmi bentov2-gateway:0.0.1 --force;

clean-auth:
	docker rm bentov2-auth --force; 

clean-web:
	docker-compose stop web;
	docker rm bentov2-web --force; \
	docker rmi bentov2-web:0.0.1 --force;

clean-drop-box:
	docker rm bentov2-drop-box --force; \
	docker rmi bentov2-drop-box:0.0.1 --force;

clean-service-registry:
	docker rm bentov2-service-registry --force; \
	docker rmi bentov2-service-registry:0.0.1 --force;

clean-katsu:
	docker rm bentov2-katsu --force; \
	docker rmi bentov2-katsu:0.0.1 --force;
	
	docker rm bentov2-katsu-db --force;

clean-logging:
	docker rm bentov2-logging --force; \
	docker rmi bentov2-logging:0.0.1 --force;

clean-drs:
	docker rm bentov2-drs --force; \
	docker rmi bentov2-drs:0.0.1 --force;

clean-variant:
	docker rm bentov2-variant --force; \
	docker rmi bentov2-variant:0.0.1 --force;

clean-notification:
	docker rm bentov2-notification --force; \
	docker rmi bentov2-notification:0.0.1 --force;

clean-federation:
	docker rm bentov2-federation --force; \
	docker rmi bentov2-federation:0.0.1 --force;

clean-event-relay:
	docker rm bentov2-event-relay --force; \
	docker rmi bentov2-event-relay:0.0.1 --force;

clean-redis:
	docker rm bentov2-redis --force

clean-wes:
	docker rm bentov2-wes --force; \
	docker rmi bentov2-wes:0.0.1 --force;


clean-all-volume-dirs:
	sudo rm -r lib/*/data




#>>>
# run authentication system setup
# make auth-setup

#<<<
.PHONY: auth-setup
auth-setup:
	$(MAKE) run-gateway
	bash $(PWD)/etc/scripts/setup.sh
	$(MAKE) clean-gateway
	$(MAKE) run-gateway



#>>>
# create non-repo directories
# make mkdir

#<<<
.PHONY: init-dirs
init-dirs:
	mkdir -p $(PWD)/tmp/secrets



#>>>
# create secrets for CanDIG services
# make docker-secrets

#<<<
.PHONY: docker-secrets
docker-secrets:
	# AuthN Admin secrets
	@echo ${BENTOV2_AUTH_ADMIN_USER} > $(PWD)/tmp/secrets/keycloak-admin-user
	@echo ${BENTOV2_AUTH_ADMIN_PASSWORD} > $(PWD)/tmp/secrets/keycloak-admin-password

	# Database
	@echo admin > $(PWD)/tmp/secrets/metadata-db-user
	@echo dev-app > $(PWD)/tmp/secrets/metadata-app-secret
	@echo devpassword123 > $(PWD)/tmp/secrets/metadata-db-secret


	docker secret create keycloak-admin-user $(PWD)/tmp/secrets/keycloak-admin-user
	docker secret create keycloak-admin-password $(PWD)/tmp/secrets/keycloak-admin-password

	docker secret create metadata-app-secret $(PWD)/tmp/secrets/metadata-app-secret
	docker secret create metadata-db-user $(PWD)/tmp/secrets/metadata-db-user
	docker secret create metadata-db-secret $(PWD)/tmp/secrets/metadata-db-secret


#>>>
# clean docker secrets

#<<<
.PHONY: clean-secrets
clean-secrets:
	rm -rf $(PWD)/tmp/secrets

	docker secret rm keycloak-admin-user
	docker secret rm keycloak-admin-password

	docker secret rm metadata-app-secret
	docker secret rm metadata-db-user
	docker secret rm metadata-db-secret

#>>>
# clean docker secrets

#<<<
.PHONY: clean-chord-services
clean-chord-services:
	rm $(PWD)/lib/*/chord_services.json


