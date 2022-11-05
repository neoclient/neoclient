ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT:=$(shell basename ${ROOT_DIR})

install:
	@poetry install

test:
	@poetry run python -m pytest ${ROOT_DIR}

typecheck:
	# TODO: Typecheck examples/ as well
	@poetry run python -m mypy ${PROJECT} tests

format:
	@poetry run python -m isort ${ROOT_DIR}
	@poetry run python -m black ${ROOT_DIR}