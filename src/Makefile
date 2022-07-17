#!/usr/bin/make -f

SHELL=/bin/bash -o pipefail
PYTHON= python3
MANAGE=$(PYTHON) manage.py
CONFIG=--configuration=$(__ENV__)

clean:
	find . -type d -name __pycache__ -empty -print0 | xargs --null --no-run-if-empty rmdir
	coverage erase

.PHONY: test tests
test tests:
	make clean
ifdef DEBUG
	pytest --black --ff --isort --blockage --instafail -n 0 --pdb -v
else
	coverage run -m pytest --black --ff --isort --blockage --instafail -n 0 --durations=25 -v
	coverage report -m
endif

.PHONY: sort
sort:
	isort -rc --atomic .

.PHONY: format
format:
	black .

.PHONY: runserver
runserver:
	$(MANAGE) runserver 0.0.0.0:8000 $(CONFIG)

.PHONY: migrate
migrate:
	@$(MANAGE) migrate $(app) $(CONFIG)

.PHONY: make-migrations
make-migrations:
	@$(MANAGE) makemigrations $(app) $(CONFIG)

.PHONY: shell
shell:
	@$(MANAGE) shell $(CONFIG)

.PHONY: compilemessages
compilemessages:
	@$(MANAGE) compilemessages

.PHONY: makemessages
makemessages:
	@$(MANAGE) makemessages --extension=html,txt,py,email

.PHONY: genoutsidedb
genoutsidedb:
	sqlacodegen $(OUTSIDE_DATA_NETLOC) >> apps/core/outside_db/models.py
