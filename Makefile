# Makefile for BentoV2

#>>>
# import and setup global variables

#<<<
env ?= .env

include $(env)
export $(shell sed 's/=.*//' $(env))

SHELL = bash

CURRENT_UID := $(shell id -u)
export CURRENT_UID


#>>>
# init chord services
#<<<
.PHONY: init-chord-services
init-chord-services:

	# create dummy auth_config.json "placeholder"
	echo "{\"data\":\"this is a placeholder and should be overwritten when the authentication service is configured. if you are reading this, see the project README, and perhaps consult the 'Makefile'\"}" > $(PWD)/lib/gateway/auth_config.json;

	# copy instance_config to gateway	
	envsubst < ${PWD}/etc/templates/instance_config.example.json > $(PWD)/lib/gateway/instance_config.json;

	# copy services json to the microservices that need it	
	envsubst < ${PWD}/etc/templates/chord_services.example.json > $(PWD)/lib/logging/chord_services.json;
	envsubst < ${PWD}/etc/templates/chord_services.example.json > $(PWD)/lib/service-registry/chord_services.json; \
	envsubst < ${PWD}/etc/templates/chord_services.example.json > $(PWD)/lib/wes/chord_services.json; \


#>>>
# create non-repo directories
#<<<
.PHONY: init-dirs
init-dirs: data-dirs 
	mkdir -p $(PWD)/tmp/secrets


#>>>
# create data directories
#<<<
data-dirs:
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
	# Swarm for docker secrets
	docker swarm init

	# Internal cluster network
	docker network create bridge-net


#>>>
# create secrets for Bento v2 services
#<<<
.PHONY: docker-secrets
docker-secrets:
	# AuthN Admin secrets
	@echo ${BENTOV2_AUTH_ADMIN_USER} > $(PWD)/tmp/secrets/keycloak-admin-user
	# temp:
	#$(MAKE) secret-keycloak-admin-password
	@echo ${BENTOV2_AUTH_ADMIN_PASSWORD} > $(PWD)/tmp/secrets/keycloak-admin-password

	docker secret create keycloak-admin-user $(PWD)/tmp/secrets/keycloak-admin-user
	docker secret create keycloak-admin-password $(PWD)/tmp/secrets/keycloak-admin-password


	# Database
	@echo ${BENTOV2_KATSU_DB_USER} > $(PWD)/tmp/secrets/metadata-db-user
	# temp:
	# $(MAKE) secret-metadata-app-secret
	# $(MAKE) secret-metadata-db-secret
	@echo ${BENTOV2_KATSU_DB_APP_SECRET} > $(PWD)/tmp/secrets/metadata-app-secret
	@echo ${BENTOV2_KATSU_DB_PASSWORD} > $(PWD)/tmp/secrets/metadata-db-secret

	docker secret create metadata-app-secret $(PWD)/tmp/secrets/metadata-app-secret
	docker secret create metadata-db-user $(PWD)/tmp/secrets/metadata-db-user
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
#<<<
run-all:
	docker-compose up -d

#>>>
# run the web service using a local copy of bento_web
# for development purposes
#<<<
run-web-dev: clean-web
	docker-compose -f docker-compose.dev.yaml up -d --force-recreate web

#>>>
# run a specified service
#<<<
run-%:
	@if [[ $* == gateway ]]; then \
		echo "Setting up gateway prerequisites"; \
		envsubst < ./lib/gateway/nginx.conf.tpl > ./lib/gateway/nginx.conf.pre; \
		if [[ ${USE_EXTERNAL_IDP} == 1 ]]; then \
			echo "Fine tuning nginx.conf to support External IDP"; \
			\
			sed '/-- Internal IDP Starts Here --/,/-- Internal IDP Ends Here --/d' ./lib/gateway/nginx.conf.pre > ./lib/gateway/nginx.conf; \
			sed -i 's/resolver 127.0.0.11/resolver 1.1.1.1 127.0.0.11/g' ./lib/gateway/nginx.conf; \
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

	docker-compose up -d $*



#>>>
# build common base images
#<<<
build-common-base:
	docker-compose -f docker-compose.base.yaml build --no-cache common-alpine-python

#>>>
# build a specified service
#<<<
build-%:
	@# Don't build auth
	@if [[ $* == auth ]]; then \
		echo "Auth doens't need to be built! Aborting --"; \
		exit 1; \
	fi

	docker-compose build --no-cache $*



#>>>
# stop all services
#<<<
stop-all:
	docker-compose down;

#>>>
# stop a specific service
#<<<
stop-%:
	docker-compose stop $*;



#>>>
# clean up common base images
#<<<
clean-common-base:
	docker rmi bentov2-common-alpine-python:0.0.1 --force;

#>>>
# clean all service containers and/or applicable images
#<<<
clean-all:
	$(foreach SERVICE, $(SERVICES), \
		$(MAKE) clean-$(SERVICE);)

#>>>
# clean a specific service container and/or applicable images

# TODO: use env variables for container versions
#<<<
clean-%:
	docker-compose stop $*;
	
	docker rm bentov2-$* --force; 
	
	@# Some services don't need their images removed
	@if [[ $* != auth && $* != redis ]]; then \
		docker rmi bentov2-$*:0.0.1 --force; \
	fi

	@# Katsu also needs it's database to be stopped
	@if [[ $* == katsu ]]; then \
		docker rm bentov2-katsu-db --force; \
	fi

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

