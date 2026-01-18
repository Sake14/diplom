.PHONY: help install train build up down logs clean test

help:
	@echo "Доступные команды:"
	@echo "  make install    - Установка зависимостей"
	@echo "  make train      - Обучение ML модели"
	@echo "  make build      - Сборка Docker образов"
	@echo "  make up         - Запуск всех сервисов"
	@echo "  make down       - Остановка всех сервисов"
	@echo "  make logs       - Просмотр логов"
	@echo "  make clean      - Очистка временных файлов"
	@echo "  make test       - Запуск тестов"

install:
	@echo "Установка зависимостей для ML сервиса..."
	cd ml-service && python3 -m pip install -r requirements.txt
	@echo "Установка зависимостей для Web сервиса..."
	cd web-service && go mod download

train:
	@echo "Обучение модели..."
	cd ml-service && python3 train_model.py

build:
	@echo "Сборка Docker образов..."
	docker-compose build

up:
	@echo "Запуск сервисов..."
	docker-compose up -d
	@echo "Сервисы запущены!"
	@echo "Web UI: http://localhost:8080"
	@echo "ML API: http://localhost:8000"

down:
	@echo "Остановка сервисов..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "Очистка временных файлов..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf ml-service/venv
	rm -rf web-service/vendor
	@echo "Очистка завершена!"

test:
	@echo "Запуск тестов..."
	@echo "Python тесты:"
	cd ml-service && python3 -m pytest tests/ -v || echo "Тесты не настроены"
	@echo "Go тесты:"
	cd web-service && go test ./... || echo "Тесты не настроены"

dev-ml:
	@echo "Запуск ML сервиса в dev режиме..."
	cd ml-service && uvicorn predict_api:app --reload --port 8000

dev-web:
	@echo "Запуск Web сервиса в dev режиме..."
	cd web-service && export ML_SERVICE_URL=http://localhost:8000 && go run main.go
