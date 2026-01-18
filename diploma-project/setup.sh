#!/bin/bash

set -e

echo "=================================="
echo "НАСТРОЙКА ПРОЕКТА"
echo "=================================="
echo ""

# Проверка Python
echo "[1/5] Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    exit 1
fi
echo "✓ Python3 найден: $(python3 --version)"

# Проверка Go
echo ""
echo "[2/5] Проверка Go..."
if ! command -v go &> /dev/null; then
    echo "❌ Go не установлен!"
    exit 1
fi
echo "✓ Go найден: $(go version)"

# Проверка Docker
echo ""
echo "[3/5] Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo "⚠ Docker не установлен - Docker режим недоступен"
    DOCKER_AVAILABLE=false
else
    echo "✓ Docker найден: $(docker --version)"
    DOCKER_AVAILABLE=true
fi

# Обучение модели
echo ""
echo "[4/5] Обучение ML модели..."
cd ml-service

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация venv и установка зависимостей
echo "Установка Python зависимостей..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "Обучение модели..."
python train_model.py

deactivate
cd ..

# Установка Go зависимостей
echo ""
echo "[5/5] Установка Go зависимостей..."
cd web-service
go mod download
cd ..

echo ""
echo "=================================="
echo "✓ НАСТРОЙКА ЗАВЕРШЕНА!"
echo "=================================="
echo ""
echo "Для запуска проекта:"
echo ""
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "Docker режим:"
    echo "  make build"
    echo "  make up"
    echo ""
fi
echo "Локальный режим:"
echo "  Terminal 1: make dev-ml"
echo "  Terminal 2: make dev-web"
echo ""
echo "Веб-интерфейс будет доступен на: http://localhost:8080"
echo "ML API будет доступен на: http://localhost:8000"
