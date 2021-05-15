ifeq "$(origin VIRTUAL_ENV)" "undefined"
	VENV=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))/venv
else
	VENV=$(VIRTUAL_ENV)
endif

VBIN=$(VENV)/bin
VLIB=$(VENV)/lib
VSRC=$(VENV)/src
PYTHON=$(VBIN)/python
PYTEST=$(VBIN)/pytest
PIP=$(VBIN)/pip
FLAKE8=$(VBIN)/flake8
PY_LIB=$(VLIB)/python*/site-packages

# Files to be staged for the dist build.
PKG_FILES=mudtrix setup.py setup.cfg requirements.txt AUTHORS CHANGES.md COPYING LICENSE MANIFEST.in README.md

all: venv build

venv: $(VENV)/bin/python
$(VENV)/bin/python:
	virtualenv -p python3 $(VENV)
	$(PIP) install .

build: venv
	$(PIP) install .
	rm -rf mudtrix.egg-info

devel: build $(PY_LIB)/mudtrix.egg-link $(FLAKE8)

$(PY_LIB)/mudtrix.egg-link: $(VENV)/bin/python setup.py setup.cfg README.md
$(PY_LIB)/mudtrix.egg-link: mudtrix/etc/development.ini
$(PY_LIB)/mudtrix.egg-link:
	$(PYTHON) setup.py develop
	cd $(PY_LIB); rm -rf mudtrix; ln -sf ../../../../mudtrix
	rm -rf mudtrix.egg-info
	touch $@

# Ignore future warning for flake8 itself
check: $(FLAKE8)
	PYTHONWARNINGS=ignore $(FLAKE8)

db: mudtrix.db
mudtrix.db: alembic.ini alembic/versions/*
	./venv/bin/alembic -x config=config.yaml upgrade head

run: mudtrix.db
	./bin/mudtrix

tests: pytest tests-clean
ifdef FTF
	$(PYTHON) setup.py test --addopts "-k $(FTF)"
else
	$(PYTHON) setup.py test
endif
	rm -rf mudtrix.egg-info

coverage: pytest tests-clean
ifdef FTF
	$(VBIN)/coverage run --source=mudtrix setup.py test --addopts "-k $(FTF)"
else
	$(VBIN)/coverage run --source=mudtrix setup.py test
endif
	rm -rf mudtrix.egg-info

coverage-report:
	 $(VBIN)/coverage report

coverage-clean:
	 $(VBIN)/coverage erase

pytest: $(PYTEST)
$(PYTEST): requirements-test.txt
	$(PIP) install -r requirements-test.txt
	$(PIP) install --no-deps pytest-postgres==0.6.0

$(FLAKE8): requirements-test.txt
	$(PIP) install -r requirements-test.txt
	$(PIP) install --no-deps pytest-postgres==0.6.0

docs:
	make -C docs man html

# Stage the files for sdist because setuptools doesn't let me filter enough
pkg-clean:
	rm -rf $(VENV)/pkg

pkg-copy: pkg-clean
	[ -d $(VENV)/pkg ] || mkdir $(VENV)/pkg
	for F in $(PKG_FILES); do cp -ar $$F $(VENV)/pkg/`basename $$F`; done
	mkdir $(VENV)/pkg/mudtrix/docs
	cp -ar $(VENV)/docs/html $(VENV)/pkg/mudtrix/docs
	cp -ar $(VENV)/docs/man $(VENV)/pkg/mudtrix/docs

dist: sdist
sdist: venv build docs pkg-copy
	[ -d dist ] || mkdir dist
	(cd $(VENV)/pkg; $(PYTHON) setup.py sdist)
	cp -af $(VENV)/pkg/dist/* dist

clean:
	find mudtrix test -name '__pycache__' -type d | xargs rm -rf
	find mudtrix test -name '*.pyc' | xargs rm -f
	rm -f mudtrix.log

# Only remove local files, not provided VIRTUAL_ENV var
dist-clean: clean
	rm -rf venv build dist mudtrix.egg-info mudtrix.db

tests-clean:
	rm -f $(VENV)/testing.sqlite $(VENV)/testing.sqlite.org

.PHONY: devel db pyramid paste sqlalchemy psycopg2 run test tests clean
.PHONY: dist-clean devel-external docs pkg-copy venv build
