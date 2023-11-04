PROJECT_ROOT := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
SETUP_CFG := $(PROJECT_ROOT)setup.cfg
PYTHON_BIN := python3.10
NAME := textology


##### Initial Development Setups and Configurations #####

# Set up initial environment for development.
.PHONY: setup
setup:
	ln -sfnv $(PROJECT_ROOT).hooks/pre-push $(PROJECT_ROOT).git/hooks/pre-push

# Create python virtual environment for development/testing.
.PHONY: venv
venv:
	$(PYTHON_BIN) -m venv $(PROJECT_ROOT).venv && \
	source $(PROJECT_ROOT).venv/bin/activate && \
	pip install -r requirements-full-dev.txt -r requirements-dev.txt -r requirements.txt && \
	echo $(PROJECT_ROOT) > .venv/lib/$(PYTHON_BIN)/site-packages/$(NAME).pth


##### Quality Assurance #####

# Check source code format for consistent patterns.
.PHONY: format
format:
	$(PYTHON_BIN) -m black --check --diff --line-length=120 $(PROJECT_ROOT) && echo Code format good to go! || \
		(echo "Please run black against files to update their format:\nblack --line-length=120 $(PROJECT_ROOT)"; exit 1)
	isort -c $(PROJECT_ROOT) && echo Import format good to go! || \
		(echo "Please run isort against files to update their format:\nisort $(PROJECT_ROOT)"; exit 1)

# Check for common lint/complexity issues.
.PHONY: lint
lint:
	pylint --rcfile setup.cfg $(NAME) examples utils setup.py

# Check documentation and code style to ensure they match expected formats.
.PHONY: style
style:
	$(PROJECT_ROOT)utils/pydocstyle_patched.py --config $(SETUP_CFG) --count $(PROJECT_ROOT) && echo Doc style good to go!
	pycodestyle --config $(SETUP_CFG) --count $(PROJECT_ROOT) && echo Code style good to go!

# Check typehints for static typing best practices.
.PHONY: typing
typing:
	mypy --config-file $(SETUP_CFG) $(PROJECT_ROOT)

# Check for common security issues/best practices.
.PHONY: security
security:
	bandit -r -c=$(PROJECT_ROOT)bandit.yaml $(PROJECT_ROOT) && echo Security good to go!

# Check full code quality suite (minus unit tests) against source.
# Does not enforce unit tests to simplify pushes, unit tests should be automated via pipelines with standardized env.
.PHONY: qa
qa: style lint typing security format

# Run basic unit tests.
.PHONY: test
test:
	pytest -n auto $(PROJECT_ROOT)


##### Builds #####

# Package the library into a pip installable.
.PHONY: wheel
wheel:
	$(PYTHON_BIN) setup.py sdist

# Clean the packages from all builds.
.PHONY: clean
clean:
	rm -r $(PROJECT_ROOT)dist $(PROJECT_ROOT)$(NAME).egg-info
