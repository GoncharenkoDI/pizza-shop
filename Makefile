.PHONY: all check ruff black test run clean clean-all venv install

# Дефолтна ціль
all: venv check run_bot

# Створення віртуального оточення
.venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip

# Інсталяція залежностей через файл-маркер
.venv/.requirements-installed: .venv requirements.txt
	.venv/bin/pip install -r requirements.txt
	@touch .venv/.requirements-installed

# Проксі-ціль для зручного виклику `make install`
install: .venv/.requirements-installed

# Спільна ціль для всіх перевірок
check: install ruff black test

# 1. Перевірка ruff
ruff: install
	.venv/bin/ruff check .

# 2. Перевірка black
black: install
	.venv/bin/black --check .

# 3. Запуск тестів
test: install
	.venv/bin/pytest

# Запуск бота
run_bot: install
	.venv/bin/python -m bot

# Очищення тимчасових файлів та кешу
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Повне очищення (разом із віртуальним оточенням)
clean-all: clean
	rm -rf .venv

# Docker command
DOCKER_NETWORK=pizza_shop_network

POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_18

BOT_CONTAINER=pizza_shop
BOT_IMAGE=goncharenkodi/pizza_shop

include .env
export $(shell sed 's/#.*//' .env)

docker_volume:
	docker volume create $(POSTGRES_VOLUME) || true

docker_net:
	docker network create $(DOCKER_NETWORK) || true

postgres_run: docker_volume docker_net
	docker run -d \
	--name $(POSTGRES_CONTAINER) \
	-e POSTGRES_USER="$(POSTGRES_USER)" \
	-e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	-e POSTGRES_DB="$(POSTGRES_DB)" \
	-p "$(POSTGRES_HOST_PORT):$(POSTGRES_CONTAINER_PORT)" \
	-v $(POSTGRES_VOLUME):/var/lib/postgresql \
	--health-cmd="pg_isready -U $(POSTGRES_USER)" \
	--health-interval=10s \
	--health-timeout=5s \
	--health-retries=5 \
	--network $(DOCKER_NETWORK) \
	postgres:18

postgres_stop:
	docker stop $(POSTGRES_CONTAINER)
	docker rm $(POSTGRES_CONTAINER)

postgres_logs:
	@docker logs $(POSTGRES_CONTAINER)

postgres_status:
	@docker ps -a --filter name=$(POSTGRES_CONTAINER) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

postgres_psql:
	@docker exec -it $(POSTGRES_CONTAINER) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

build:
	docker build \
	-t "$(BOT_IMAGE)" \
	--platform linux/amd64,linux/arm64 \
	-f Dockerfile \
	.

push:
	docker push $(BOT_IMAGE)

run: docker_net
	docker run -d \
	--name $(BOT_CONTAINER) \
	--restart unless-stopped \
	-e POSTGRES_HOST="$(POSTGRES_CONTAINER)" \
	-e POSTGRES_PORT="$(POSTGRES_CONTAINER_PORT)" \
	-e POSTGRES_USER="$(POSTGRES_USER)" \
	-e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	-e POSTGRES_DB="$(POSTGRES_DB)" \
	-e LP_TIMEOUT="$(LP_TIMEOUT)" \
	-e TELEGRAM_TOKEN="$(TELEGRAM_TOKEN)" \
	--network $(DOCKER_NETWORK) \
	$(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER)
	docker rm $(BOT_CONTAINER)

logs:
	@docker logs $(BOT_CONTAINER)

status:
	@docker ps -a --filter name=$(BOT_CONTAINER) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
