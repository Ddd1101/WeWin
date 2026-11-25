# Development commands run from the repository; production units are already installed.
PYTHON ?= python3

.PHONY: help install-backend install-frontend run-backend run-frontend build-frontend start-services stop-services status
help:
	@echo "Development: install-backend install-frontend run-backend run-frontend build-frontend"
	@echo "Production: start-services stop-services status (systemd)"

install-backend:
	cd Server && $(PYTHON) -m pip install -r requirements.txt

install-frontend:
	cd Page && npm ci

run-backend:
	cd Server && $(PYTHON) manage.py runserver 127.0.0.1:8003

run-frontend:
	cd Page && npm run dev

build-frontend:
	cd Page && npm run build

start-services:
	bash start.sh

stop-services:
	bash stop.sh

status:
	$(PYTHON) deploy/service_control.py all status
