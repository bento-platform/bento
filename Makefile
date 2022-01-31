# Makefile for BentoV2

#>>>
# import and setup global environment variables
#<<<
env ?= .env
gohan_env ?= ./lib/gohan/.env

include $(env)
include $(gohan_env)
export $(shell sed 's/=.*//' $(env))
export $(shell sed 's/=.*//' $(gohan_env))

#>>>
# set default shell
#<<<
SHELL = bash

#>>>
# provide host-level user id as an 
# environment variable for containers to use
#<<<
CURRENT_UID := $(shell id -u)
export CURRENT_UID

#>>>
# provide a timestamp of command execution time
# as an environment variable for logging
#<<<
EXECUTED_NOW=$(shell date +%FT%T%Z)
export EXECUTED_NOW


#>>>
# init chord service configuration files
#<<<
.PHONY: init-chord-services
init-chord-services:
	@echo "-- Initializing CHORD service configuration files  --"

	@# create dummy auth_config.json "placeholder"
	@echo "- Creating a "dummy" auth_config.json to be overwritten later.."
	@echo "{\"data\":\"this is a placeholder and should be overwritten when the authentication service is configured. if you are reading this, see the project README, and perhaps consult the 'Makefile'\"}" > $(PWD)/lib/gateway/auth_config.json;

	@# copy instance_config to gateway	
	@echo "- Copying instance_config.json to lib/gateway"
	@envsubst < ${PWD}/etc/templates/instance_config.json.tpl > $(PWD)/lib/gateway/instance_config.json;

	@# copy services json to the microservices that need it	
	@echo "- Providing a complete chord_services.json to lib/[logging, service-registry, wes]"
	@envsubst < ${PWD}/etc/templates/chord_services.example.json > $(PWD)/lib/logging/chord_services.json;
	@envsubst < ${PWD}/etc/templates/chord_services.example.json > $(PWD)/lib/service-registry/chord_services.json;
	@envsubst < ${PWD}/etc/templates/chord_services.example.json > $(PWD)/lib/wes/chord_services.json;

	@echo "-- Done --"


#>>>
# create non-repo directories
#<<<
.PHONY: init-dirs
init-dirs: data-dirs 
	@echo "-- Initializing temporary and data directories --"
	@echo "- Creating temporary secrets dir"
	mkdir -p $(PWD)/tmp/secrets

	@echo "- Creating temporary deployment logs dir"
	mkdir -p $(PWD)/tmp/logs/deployments


#>>>
# create data directories
#<<<
data-dirs:
	@echo "- Creating data dirs"
	mkdir -p ${BENTOV2_AUTH_VOL_DIR}
	mkdir -p ${BENTOV2_KATSU_DB_VOL_DIR}
	mkdir -p ${BENTOV2_NOTIFICATION_VOL_DIR}
	mkdir -p ${BENTOV2_FEDERATION_VOL_DIR}
	mkdir -p ${BENTOV2_WES_VOL_DIR}
	mkdir -p ${BENTOV2_REDIS_VOL_DIR}






#>>>
# initialize docker prerequisites
#<<<
.PHONY: init-docker
init-docker:
	@# Swarm for docker secrets
	@echo "-- Initializing Docker Swarm for docker secrets (this may crash if already set) --"
	@docker swarm init &

	@# Internal cluster network
	@echo "-- Initializing Docker Network (this may crash if already set) --"
	@docker network create bridge-net


init-gohan:
	@cd lib && \
	\
	if [ ! -d "./gohan" ]; then \
		echo "-- Cloning Gohan --" ; \
		git clone ${GOHAN_REPO} ; \
	else \
		echo "-- Gohan already cloned --" ; \
	fi && \
	\
	cd gohan && \
	\
	git fetch && \
	git checkout "${GOHAN_BRANCH}" && \
	git pull && \
	if [[ -n "${GOHAN_TAG}" ]]; then \
    	git checkout tags/${GOHAN_TAG} ; \
	else \
		echo "-- No git tag provided - skipping 'git checkout tags/...'" ; \
	fi


#>>>
# create secrets for Bento v2 services
#<<<
.PHONY: docker-secrets
docker-secrets:
	@echo "-- Creating Docker Secrets --"

	@# AuthN Admin secrets
	@# User:
	@echo "- Creating Admin User" && \
		echo ${BENTOV2_AUTH_ADMIN_USER} > $(PWD)/tmp/secrets/keycloak-admin-user && \
		docker secret create keycloak-admin-user $(PWD)/tmp/secrets/keycloak-admin-user &

	@# Password:
	@# TODO: use 'secret' generator
	@#$(MAKE) secret-keycloak-admin-password
	@echo "- Creating Admin Password" && \
		echo ${BENTOV2_AUTH_ADMIN_PASSWORD} > $(PWD)/tmp/secrets/keycloak-admin-password && \
		docker secret create keycloak-admin-password $(PWD)/tmp/secrets/keycloak-admin-password &


	@# Database
	@# User:
	@echo "- Creating Metadata User" && \
		echo ${BENTOV2_KATSU_DB_USER} > $(PWD)/tmp/secrets/metadata-db-user && \
		docker secret create metadata-db-user $(PWD)/tmp/secrets/metadata-db-user &

	@# Passwords:
	@# TODO: use 'secret' generator
	@# $(MAKE) secret-metadata-app-secret
	@# $(MAKE) secret-metadata-db-secret
	@echo "- Creating Metadata Password/Secrets" && \
		echo ${BENTOV2_KATSU_DB_APP_SECRET} > $(PWD)/tmp/secrets/metadata-app-secret && \
		docker secret create metadata-app-secret $(PWD)/tmp/secrets/metadata-app-secret && \
		echo ${BENTOV2_KATSU_DB_PASSWORD} > $(PWD)/tmp/secrets/metadata-db-secret && \
		docker secret create metadata-db-secret $(PWD)/tmp/secrets/metadata-db-secret



#>>>
# run authentication system setup
#<<<
.PHONY: auth-setup
auth-setup:
	bash $(PWD)/etc/scripts/setup.sh
	$(MAKE) clean-gateway
	$(MAKE) run-gateway



#>>>
# run all services
# - each service runs (and maybe builds) on it's own background process to complete faster
#<<<
run-all:
	$(foreach SERVICE, $(SERVICES), \
		$(MAKE) run-$(SERVICE) &) 

	watch -n 2 'docker ps'



#>>>
# run the web service using a local copy of bento_web
# for development purposes
#
#	see docker-compose.dev.yaml
#<<<
run-web-dev: clean-web
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate web

#>>>
# run the gateway service that utilizes the local idp hostname as an alias
# for development purposes
#
#	see docker-compose.dev.yaml
#<<<
run-gateway-dev: clean-gateway
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate gateway

#>>>
# ...
#	see docker-compose.dev.yaml
#<<<
run-variant-dev: clean-variant
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate variant

#>>>
# ...
#	see docker-compose.dev.yaml
#<<<
run-katsu-dev: clean-katsu
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate katsu

#>>>
# ...
#	see docker-compose.dev.yaml
#<<<
run-federation-dev: 
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate federation

#>>>
# ...
#	see docker-compose.dev.yaml
#<<<
run-wes-dev: 
	#clean-wes
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate wes

#>>>
# ...
#	see docker-compose.dev.yaml
#<<<
run-drs-dev: 
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate drs


#>>>
# run a specified service
#<<<
run-%:
	@if [[ $* == gateway ]]; then \
		echo "Setting up gateway prerequisites"; \
		envsubst < ./lib/gateway/nginx.conf.tpl > ./lib/gateway/nginx.conf.pre; \
		if [[ ${BENTOV2_USE_EXTERNAL_IDP} == 1 ]]; then \
			echo "Fine tuning nginx.conf to support External IDP"; \
			\
			sed '/-- Internal IDP Starts Here --/,/-- Internal IDP Ends Here --/d' ./lib/gateway/nginx.conf.pre > ./lib/gateway/nginx.conf; \
			\
			rm ./lib/gateway/nginx.conf.pre; \
		else \
			cat ./lib/gateway/nginx.conf.pre > ./lib/gateway/nginx.conf; \
			rm ./lib/gateway/nginx.conf.pre; \
		fi \
	elif [[ $* == web ]]; then \
		echo "Cleaning web before running"; \
		$(MAKE) clean-web; \
	fi

	@if [[ $* == auth && ${BENTOV2_USE_EXTERNAL_IDP} == 1 ]]; then \
		echo "Auth doens't need to be built! Skipping --"; \
		exit 1; \
	fi

	@mkdir -p tmp/logs/${EXECUTED_NOW}/$*

	@if [[ $* == gohan ]]; then \
		echo "-- Running $* : see tmp/logs/${EXECUTED_NOW}/$*/ run logs for details! --" && \
		cd lib/gohan && \
		$(MAKE) clean-api &> ../../tmp/logs/${EXECUTED_NOW}/$*/api_run.log && \
		$(MAKE) run-api &>> ../../tmp/logs/${EXECUTED_NOW}/$*/api_run.log && \
		\
		$(MAKE) run-elasticsearch &> ../../tmp/logs/${EXECUTED_NOW}/$*/elasticsearch_run.log & \
	else \
		echo "-- Running $* : see tmp/logs/${EXECUTED_NOW}/$*/run.log for details! --" && \
		docker-compose up -d $* &> tmp/logs/${EXECUTED_NOW}/$*/run.log & \
	fi



#>>>
# build common base images
#<<<
build-common-base:
	docker-compose -f docker-compose.base.yaml build --no-cache common-alpine-python
	#docker-compose -f docker-compose.base.yaml build --no-cache common-debian-python

#>>>
# build all service images
# - each service building runs on it's own background process to complete faster
#<<<
build-all:
	$(foreach SERVICE, $(SERVICES), \
		$(MAKE) build-$(SERVICE) &) 
	
	watch -n 2 'docker ps'


#>>>
# build a specified service
#<<<
build-%:
	@# Don't build auth
	@if [[ $* == auth ]]; then \
		echo "Auth doens't need to be built! Aborting --"; \
		exit 1; \
	fi

	@mkdir -p tmp/logs/${EXECUTED_NOW}/$* 
	@echo "-- Building $* --" && \
		docker-compose build --no-cache $* &> tmp/logs/${EXECUTED_NOW}/$*/build.log



#>>>
# stop all services
#<<<
stop-all:
	docker-compose down;

	cd lib/gohan && \
	docker-compose down && \
	cd ../.. ;

#>>>
# stop a specific service
#<<<
stop-%:
	docker-compose stop $*;



#>>>
# inspect a specific service
#<<<
inspect-%:
	watch 'docker logs bentov2-$* | tail -n 25'



#>>>
# clean up common base images
#<<<
clean-common-base:
	docker rmi bentov2-common-alpine-python:0.0.1 --force;

#>>>
# clean all service containers and/or applicable images
# - each service cleaning runs on it's own background process to complete faster
#<<<
clean-all:
	$(foreach SERVICE, $(SERVICES), \
		$(MAKE) clean-$(SERVICE) &)

#>>>
# clean a specific service container and/or applicable images

# TODO: use env variables for container versions
#<<<
clean-%:
	@mkdir -p tmp/logs/${EXECUTED_NOW}/$* && \
		echo "-- Stopping $* --" && \
		docker-compose stop $* &> tmp/logs/${EXECUTED_NOW}/$*/clean.log
	
	@echo "-- Removing bentov2-$* container --" && \
		docker rm bentov2-$* --force &>> tmp/logs/${EXECUTED_NOW}/$*/clean.log
	
	@# Some services don't need their images removed
	@if [[ $* != auth && $* != redis ]]; then \
		docker rmi bentov2-$*:0.0.1 --force; \
	fi &>> tmp/logs/${EXECUTED_NOW}/$*/clean.log

	@# Katsu also needs it's database to be stopped
	@if [[ $* == katsu ]]; then \
		docker rm bentov2-katsu-db --force; \
	fi &>> tmp/logs/${EXECUTED_NOW}/$*/clean.log

#>>>
# clean data directories
#<<<
clean-all-volume-dirs:
	sudo rm -r lib/*/data

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
# clean docker services
#<<<
.PHONY: clean-chord-services
clean-chord-services:
	rm $(PWD)/lib/*/chord_services.json



#>>>
# tests
#<<<
run-tests: \
		run-unit-tests \
		run-integration-tests

run-unit-tests:
	@echo "-- No unit tests yet! --"

run-integration-tests:
	@echo "-- Running integration tests! --"
	@$(PWD)/etc/tests/integration/run_tests.sh 10 firefox True
	


# -- Utils --

#>>>
# create a random secret and add it to tmp/secrets/$secret_name
#<<<
secret-%:
	@dd if=/dev/urandom bs=1 count=16 2>/dev/null \
		| base64 | rev | cut -b 2- | rev | tr -d '\n\r' > $(PWD)/tmp/secrets/$*

#>>>
# docker tooling
#<<<
clean-dangling-images:
	docker rmi $(docker images -f "dangling=true" -q)
clean-exited-containers:
	docker rm $(docker ps -a -f status=exited -q)
