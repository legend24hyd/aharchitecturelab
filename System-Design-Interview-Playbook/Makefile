.PHONY: html epub docx pdf lint all

PYTHON ?= python3
BOOK_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

lint:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" lint

html:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" html

epub:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" epub

docx:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" docx

pdf:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" pdf

all:
	$(PYTHON) "$(BOOK_DIR)tools/build.py" all
