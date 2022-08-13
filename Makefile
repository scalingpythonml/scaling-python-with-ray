CONFIG=compose/development.yml
PROD_CONFIG=compose/production.yml
PROJECT=spacebeaver
DOCKERUSER=holdenk

ifeq (shell, $(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(lastword $(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif


.PHONY: format
format:
	python -m black ./src

.PHONY: crossbuild
crossbuild:
	docker buildx bake -f $(PROD_CONFIG) --progress=plain --set *.platform=linux/arm64,linux/amd64 --set app.tags.image=${DOCKERUSER}/$(PROJECT)-web app --push

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
	@docker-compose -f $(CONFIG) -p $(PROJECT) exec -T app make test

.PHONY: make-migrations
make-migrations: up
	@docker-compose -f $(CONFIG) -p $(PROJECT) exec -T app make migrate
	@docker-compose -f $(CONFIG) -p $(PROJECT) exec -T app make make-migrations
