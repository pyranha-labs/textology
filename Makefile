# Additional recipes for Python based development.
-include python.mk

# Recipes unique to this project.
UPSTREAM := git@github.com:pyranha-labs/textology.git
PYLINT_EXTRAS := examples

##### Initial Development Setups and Configurations #####

# Set up initial environment for development.
GIT_PROJECT_ROOT := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
.PHONY: setup
setup:
	ln -sfnv $(GIT_PROJECT_ROOT).hooks/pre-push $(GIT_PROJECT_ROOT).git/hooks/pre-push
	-git remote add upstream $(UPSTREAM)
	git fetch upstream
	@echo "🏆 Git set up complete!"
	curl https://raw.githubusercontent.com/pyranha-labs/build-tools/refs/heads/main/python.mk -o python.mk
	make clean-venv venv
	. $(GIT_PROJECT_ROOT)activate && make qa test
