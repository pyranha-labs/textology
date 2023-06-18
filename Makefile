GIT_DIR := $(shell git rev-parse --show-toplevel)
SETUP_CFG := $(GIT_DIR)/setup.cfg
PYTHON_BIN := python3.10
NAME := textology


##### Initial Development Setups and Configurations #####

# Set up initial environment for development.
.PHONY: setup
setup:
	ln -sfnv $(GIT_DIR)/.hooks/pre-push $(GIT_DIR)/.git/hooks/pre-push

# Create python virtual environment for development/testing.
.PHONY: venv
venv:
	$(PYTHON_BIN) -m venv $(GIT_DIR)/.venv && \
	source $(GIT_DIR)/.venv/bin/activate && \
	pip install -r requirements-dev.txt -r requirements.txt && \
	echo $(GIT_DIR) > .venv/lib/python3.10/site-packages/textology.pth


##### Quality Assurance #####

# Check source code format for consistent patterns.
.PHONY: format
format:
	$(PYTHON_BIN) -m black --check --diff --line-length=120 $(GIT_DIR) || echo Please run "black --line-length=120" against files to update their format.
	isort -c $(GIT_DIR) || echo Please run "isort" against files to update their format.

# Check for common lint/complexity issues.
.PHONY: lint
lint:
	pylint --rcfile setup.cfg $(NAME) examples setup.py

# Check documentation and code style to ensure they match expected formats.
.PHONY: style
style:
	pydocstyle --config $(SETUP_CFG) --count $(GIT_DIR)
	pycodestyle --config $(SETUP_CFG) --count $(GIT_DIR)

# Check typehints for static typing best practices.
.PHONY: typing
typing:
	mypy --config-file $(SETUP_CFG) $(GIT_DIR)

# Check typehints for static typing best practices.
.PHONY: security
security:
	bandit -r -c=$(GIT_DIR)/bandit.yaml $(GIT_DIR)

# Run full QA suite against source code.
.PHONY: qa
qa: lint style typing security format

# Run basic unit tests.
.PHONY: test
test:
	pytest -n auto $(GIT_DIR)


##### Builds #####

# Package the library into a pip installable.
.PHONY: wheel
wheel:
	$(PYTHON_BIN) setup.py sdist

# Clean the packages from all builds.
.PHONY: clean
clean:
	rm -r $(GIT_DIR)/dist $(GIT_DIR)/textology.egg-info
