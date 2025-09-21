# Contributor Guide

## How can I contribute?

Contributions can be as large or as small as you like! Example of common contributions:

- Report an issue
- Fix an issue
- Add a feature
- Improve documentation

A special thanks to everyone who donates their time to contribute!


## Getting Started

### Makefile

Mentioned throughout this guide are the use of commands/recipes from the [Makefile](Makefile). It contains
all the most common operations used during development. The recipes are not required to be used for set up,
however they are required for commit hooks, and they greatly simplify all development processes. You can
reference the recipes in the file directly for any manual steps. For more information about `make`, refer to:  
[Make Software](https://en.wikipedia.org/wiki/Make_(software))

### Development Setup

To make code or documentation contributions you will need to set up the project locally. You can follow these steps:

1. Clone your fork with `git clone <path to fork>` and enter the project directory.
1. Run `make setup` to set up git configurations (such as hooks and upstream) and python environment.
    - `make clean-venv` `make venv` will run automatically to create a fresh virtual environment.
    - `make qa` and `make test` will run automatically to ensure environment was set up correctly.
    - If any recipes, they can be rerun manually without repeating `make setup`.
1. Activate the development environment with `. activate`.
   - Alternatively, you can use `. .venv/bin/activate` to activate the environment.

The environment can now be deactivated at anytime with `deactivate`, or reactivated with `. activate`.

## Open a Pull Request

This project uses a forking workflow for contributions. When in doubt, start with the
[GitHub flow](https://guides.github.com/introduction/flow/) for all new Pull Requests (PRs). If new to forking, refer to
[GitHub forking](https://guides.github.com/activities/forking/) for more information about this workflow.
If new to branching, refer to [Learn Git Branching](https://learngitbranching.js.org/) for an interactive tutorial.

### Before a Pull Request

This project strives to provide a great code review experience for everyone. A great code review helps not only
the maintainers save time, but most importantly the contributors. In order to help achieve this goal,
please follow the included checklist.

  - [ ] Ensure your code passes all quality checks for scalability (`make qa`).
  - [ ] Ensure your code passes all tests for stability (`make test`).
  - [ ] Verify your code follows the styleguides in this document, and the rest of the codebase, for consistency.
  - [ ] Verify your commit is granular, and represents a single logical change, for maintainability.
    - Improves the review experience for both contributor and maintainer.
    - Simplifies future operations, such as cherry-picking, log searches, diffs, etc.

Many of these steps will run automatically when you push your changes, but it is still important to verify
the results before opening a PR. This will help expedite the review process, and guarantee the best experience
for everyone.

### After a Pull Request

Code will be reviewed by one or more maintainers before being merged. In order to help maintain quality,
or in the event that automated tooling does not catch everything, maintainers may ask for additional
improvements before approving a PR. To help provide a smooth experience for everyone, please complete the self
checklist populated in the PR body. Maintainers are encouraged to wait until the checklist is complete
before reviewing a PR.

During the review process, some common requests from maintainers may include, but are not limited to:
- Handle edge cases, to improve scalability.
- Add more detail to documentation, to improve maintainability and readability.
- Include additional tests, to guarantee stability.

Do not be discouraged if a maintainer asks for changes, these are common to ensure the highest quality possible during
the life of the project. Even maintainers have to make changes to their code during the review process. No one is
perfect, but as a team we can create the best possible solutions.


## Styleguides

### Documentation Styleguide

This project follows [Google Python Styleguide](https://google.github.io/styleguide/pyguide.html) for all documentation.
The `pydocstyle` tool from PyCQA is used to help automatically enforce this style in the codebase.

In order to help maintain consistency and readability, or in the event that automated tooling does not catch everything,
maintainers may ask for additional improvements before approving a PR.

### Python Styleguide

This project follows [Google's Python Styleguide](https://google.github.io/styleguide/pyguide.html) for all Python code.
The `pycodestyle` and `pylint` tools are used to help automatically enforce these guidelines in the codebase.
[Black](https://github.com/python/black) is also enforced on all Python code to maximize consistency, and reduce
conflicts due to personal opinions about formatting as much as possible.

In order to help maintain consistency and readability, or in the event that automated tooling does not catch everything,
maintainers may ask for additional improvements before approving a PR.
