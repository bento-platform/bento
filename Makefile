# Makefile for BentoV2

#>>>
# import and setup global environment variables
#<<<
default_config_env ?= ./etc/default_config.env
local_env ?= local.env
env ?= ./etc/bento.env
# gohan_env ?= ./lib/gohan/.env


# a lot of the commands are ran before the gohan and public env files exist
# "-" sign prevents make from failing if the file does not exist
include $(default_config_env)
include $(local_env)
include $(env)
# -include $(gohan_env)

export $(shell sed 's/=.*//' $(env))
# export $(shell sed 's/=.*//' $(gohan_env))
export $(shell sed 's/=.*//' $(local_env))


#>>>
# set default shell
#<<<
SHELL = bash

#>>>
# architecture
#<<<
OS_NAME := $(shell uname -s | tr A-Z a-z)
export OS_NAME

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

	mkdir -p ${BENTOV2_ROOT_DATA_DIR}

	mkdir -p ${BENTOV2_AUTH_VOL_DIR}
	mkdir -p ${BENTOV2_DROP_BOX_VOL_DIR}
	mkdir -p ${BENTOV2_KATSU_DB_PROD_VOL_DIR}
	mkdir -p ${BENTOV2_NOTIFICATION_VOL_DIR}
	mkdir -p ${BENTOV2_WES_VOL_DIR}
	mkdir -p ${BENTOV2_REDIS_VOL_DIR}

	mkdir -p ${BENTOV2_GOHAN_API_VCF_PATH}
	mkdir -p ${BENTOV2_GOHAN_API_GTF_PATH}
	mkdir -p ${BENTOV2_GOHAN_ES_DATA_DIR}



#>>>
# create secrets for Bento v2 services
#<<<
.PHONY: docker-secrets
docker-secrets:
	@echo "-- Creating Docker Secrets --"

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
		docker secret create metadata-app-secret $(PWD)/tmp/secrets/metadata-app-secret &
		echo ${BENTOV2_KATSU_DB_PASSWORD} > $(PWD)/tmp/secrets/metadata-db-secret && \
		docker secret create metadata-db-secret $(PWD)/tmp/secrets/metadata-db-secret



#>>>
# run all services
# - each service runs (and maybe builds) on it's own background process to complete faster
#<<<
run-all:
	$(foreach SERVICE, $(SERVICES), \
		$(MAKE) run-$(SERVICE) &)

	watch -n 2 'docker ps'




#>>>
# inspect a specific service
#<<<
inspect-%:
	watch 'docker logs bentov2-$* | tail -n 25'



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
	@mkdir -p tmp/logs/${EXECUTED_NOW}/$*

	@echo "-- Removing bentov2-$* container --" && \
		docker rm bentov2-$* --force >> tmp/logs/${EXECUTED_NOW}/$*/clean.log 2>&1

	@# Some services don't need their images removed
	@if [[ $* != auth && $* != redis ]]; then \
		docker rmi bentov2-$*:0.0.1 --force; \
	fi >> tmp/logs/${EXECUTED_NOW}/$*/clean.log 2>&1

	@# Katsu also needs it's database to be stopped
	@if [[ $* == katsu ]]; then \
		docker rm bentov2-katsu-db --force; \
	fi >> tmp/logs/${EXECUTED_NOW}/$*/clean.log 2>&1



#>>>
# clean data directories
#<<<
clean-all-volume-dirs:
	sudo rm -r ${BENTOV2_ROOT_DATA_DIR}

#>>>
# clean docker secrets
#<<<
.PHONY: clean-secrets
clean-secrets:
	rm -rf $(PWD)/tmp/secrets

	docker secret rm metadata-app-secret
	docker secret rm metadata-db-user
	docker secret rm metadata-db-secret


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
	@$(PWD)/etc/tests/integration/run_tests.sh 10 firefox False



# -- Utils --

#>>>
# create a random secret and add it to tmp/secrets/$secret_name
#<<<
secret-%:
	@dd if=/dev/urandom bs=1 count=16 2>/dev/null \
		| base64 | rev | cut -b 2- | rev | tr -d '\n\r' > $(PWD)/tmp/secrets/$*

# logs
clean-logs:
	cd tmp/logs/ && \
	rm -rf * && \
	cd ../.. ;

#>>>
# docker tooling
#<<<
clean-dangling-images:
	docker rmi $(docker images -f "dangling=true" -q)
clean-exited-containers:
	docker rm $(docker ps -a -f status=exited -q)

#>>>
# patch records in DRS database after the change in path from /drs/chord_drs/ to /drs/bento_drs/
# This needs to be done only once, for installations prior v2.6.5
#<<<
patch-drs-db:
	sqlite3 ${BENTOV2_DRS_PROD_VOL_DIR}/db/db.sqlite3 \
		"UPDATE drs_object SET location = REPLACE(location, 'chord_drs', 'bento_drs')" && \
	sqlite3 ${BENTOV2_DRS_DEV_VOL_DIR}/db/db.sqlite3 \
		"UPDATE drs_object SET location = REPLACE(location, 'chord_drs', 'bento_drs')"
