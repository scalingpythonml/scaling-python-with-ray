CONFIG=compose/development.yml
PROJECT=spacebeaver

ifeq (shell, $(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(lastword $(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif



.PHONY: up
up: export DOCKER_BUILDKIT := 1
up: export COMPOSE_DOCKER_CLI_BUILD=1
up:
	@docker-compose -f $(CONFIG) -p $(PROJECT) up -d

.PHONY: stop
stop:
	@docker-compose -f $(CONFIG) -p $(PROJECT) stop

.PHONY: rebuild
rebuild: export DOCKER_BUILDKIT := 1
rebuild: export COMPOSE_DOCKER_CLI_BUILD=1
rebuild:
	@docker-compose -f $(CONFIG) -p $(PROJECT) down
	@docker-compose -f $(CONFIG) -p $(PROJECT) pull --include-deps
	@docker-compose -f $(CONFIG) -p $(PROJECT) build

.PHONY: shell
shell:
	@docker-compose -f $(CONFIG) -p $(PROJECT) exec $(RUN_ARGS) /bin/bash

.PHONY: test
test: up
	@docker-compose -f $(CONFIG) -p $(PROJECT) exec app make test
