APP=bigleague
IMAGE=twobradleys/bigleague
VERSION=1.0
INSTALL_DIR=/opt/$(APP)
POSTGRES_USER?=postgres
PGPASSWORD?=localpasswordnotforproduction
POSTGRES_HOST?=db
POSTGRES_ENV?= \
			   -e POSTGRES_USER=$(POSTGRES_USER) \
			   -e PGPASSWORD=$(PGPASSWORD) \
			   -e POSTGRES_HOST=$(POSTGRES_HOST) 

.PHONY: image shell test test-$(APP) run-$(APP)

image: Dockerfile
	docker build -t $(IMAGE):$(VERSION) .
	docker tag $(IMAGE):$(VERSION) $(IMAGE):latest
		
shell: image
	docker run \
		--rm \
		--name $(APP)-shell \
		-P \
		-e APP_CONFIG=$(INSTALL_DIR)/config/production.yaml \
		-e DEBUG=1 \
		$(POSTGRES_ENV) \
		-e PORT=5200 \
		-p 5200:5200 \
		--link bigleague-db:db \
		-v `pwd`/tests:/tests \
		-it $(IMAGE):$(VERSION) \
		bash

db-shell: image
	docker run \
		--rm \
		--name $(APP)-shell \
		-P \
		-e APP_CONFIG=$(INSTALL_DIR)/config/production.yaml \
		--link bigleague-db:db \
		$(POSTGRES_ENV) \
		-it $(IMAGE):$(VERSION) \
		psql -h $(POSTGRES_HOST) -U $(POSTGRES_USER) bigleague

test: image
	docker run \
		--rm \
		--name $(APP)-test \
		-e APP_CONFIG=$(INSTALL_DIR)/config/test.yaml \
		-e DEBUG=1 \
		--link bigleague-db:db \
		$(POSTGRES_ENV) \
		-v `pwd`/tests:/tests \
		-it $(IMAGE):$(VERSION) \
		bash -c 'echo "Running tests..." && cd $(INSTALL_DIR) && flake8 . && cd /tests && flake8 . && py.test'

bootstrap-db: image
	docker run \
		--rm \
		--name $(APP)-bootstrap-prep \
		-e APP_CONFIG=$(INSTALL_DIR)/config/test.yaml \
		$(POSTGRES_ENV) \
		--link bigleague-db:db \
		-v `pwd`/bootstrap_db:/bootstrap_db \
		-it $(IMAGE):$(VERSION) \
		bash -c 'echo "Prepping DB..." && /bootstrap_db/init.sh'
	docker run \
		--rm \
		--name $(APP)-bootstrap-migrate \
		-e APP_CONFIG=$(INSTALL_DIR)/config/test.yaml \
		$(POSTGRES_ENV) \
		--link bigleague-db:db \
		-it $(IMAGE):$(VERSION) \
		bash -c 'echo "Running migrations..." && cd $(INSTALL_DIR) && alembic downgrade -1 ; alembic upgrade head'

bootstrap-remote-db: image
	docker run \
		--rm \
		--name $(APP)-bootstrap-migrate \
		-e APP_CONFIG=$(INSTALL_DIR)/config/production.yaml \
		$(POSTGRES_ENV) \
		-it $(IMAGE):$(VERSION) \
		bash -c 'echo "Running migrations..." && cd $(INSTALL_DIR) && alembic downgrade -1 && alembic upgrade head'

serve: image
	-docker kill $(APP)-server
	-docker rm $(APP)-server
	docker run \
		--name $(APP)-server \
		--rm \
		-e APP_CONFIG=$(INSTALL_DIR)/config/production.yaml \
		-e DEBUG=1 \
		$(POSTGRES_ENV) \
		-e PORT=5200 \
		-p 5200:5200 \
		--link bigleague-db:db \
		-it $(IMAGE):$(VERSION) \
		$(APP)-serve

run-db:
	docker run \
		--name bigleague-db \
		-e POSTGRES_PASSWORD=$(PGPASSWORD) \
		-d \
		postgres
