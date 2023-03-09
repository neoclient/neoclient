ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT:=$(shell basename ${ROOT_DIR})

install:
	@poetry install

test:
	@poetry run python -m pytest ${ROOT_DIR}

typecheck:
	@poetry run python -m mypy ${PROJECT}

format:
	@poetry run python -m isort ${ROOT_DIR}
	@poetry run python -m black ${ROOT_DIR}

lint:
	@poetry run python -m pylint ${PROJECT} tests
