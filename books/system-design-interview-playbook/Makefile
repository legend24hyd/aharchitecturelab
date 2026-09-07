.PHONY: html epub lint check-tools

PYTHON ?= python3
BOOK_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

html:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" html

epub:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" epub

lint:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" lint

check-tools:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" check-tools
