APP_NAME = tfj
VENV_PREFIX = $(shell echo $(APP_NAME) | tr [a-z] [A-Z])
VENV_NAME = py36-$(APP_NAME)
VERSION = $(shell python setup.py --version)


PIP = $(WORKON_HOME)/$(VENV_NAME)/bin/pip3
PYTHON = $(WORKON_HOME)/$(VENV_NAME)/bin/python3
VIRTUALENV = $(PYENV_ROOT)/versions/3.6.0/bin/virtualenv


# avoid flake8 default ignore list
LINT_OPTION = --max-line-length 180 --ignore _ --import-order-style=edited --application-package-names=ma --application-import-names=core --exclude=vendors/


init: init-venv update-venv init-runtime


init-dev: init
	$(PIP) install -Ur requirements-dev.txt


init-venv:
	test -d $(WORKON_HOME)/$(VENV_NAME) || $(VIRTUALENV) $(WORKON_HOME)/$(VENV_NAME)


update-venv:
	true || true


deinit:
	rm -rf $(WORKON_HOME)/$(VENV_NAME)
	rm -rf vendors


lint:
	$(WORKON_HOME)/$(VENV_NAME)/bin/flake8 $(LINT_OPTION) .


test: lint
	PYTHONPATH=.:vendors $(WORKON_HOME)/$(VENV_NAME)/bin/py.test tests


test-debug: lint
	$(WORKON_HOME)/$(VENV_NAME)/bin/py.test --ipdb tests


assets:
	true || true


coverage: lint
	PYTHONPATH=.:vendors $(WORKON_HOME)/$(VENV_NAME)/bin/py.test --cov . --cov-report term-missing --cov-report xml --junitxml=junit-coverage.xml --cov-config .coveragerc tests


clean:
	true || true


init-runtime:  ## Initialize application vendors dependencies
	mkdir -p vendors && $(PIP) install -t vendors -Ur requirements.txt


build:  init-runtime
	echo $(VERSION) > VERSION
	echo $(VERSION) > latest
	test -e dist/$(APP_NAME)-$(VERSION).tar.gz || ($(PYTHON) setup.py sdist)
	test -e dist/$(APP_NAME)-$(VERSION).tar.gz || (mv dist/$(APP_NAME)-$(shell python setup.py --version).tar.gz dist/$(APP_NAME)-$(VERSION).tar.gz)


get-artifact-name:  ## Return the build artifact filename
	echo $(APP_NAME)-$(VERSION).tar.gz

.SILENT: deinit init init-venv update-venv init-dev -prod build distribute run lint test test-debug coverage clean get-artifact-name build
.PHONY: deinit init init-venv update-venv init-dev -prod build distribute run lint test test-debug coverage clean get-artifact-name build
