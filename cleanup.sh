#!/bin/bash

# Полная очистка проекта с интерактивным подтверждением

echo "════════════════════════════════════════════════════════════"
echo "  🧹 ПОЛНАЯ ОЧИСТКА ПРОЕКТА"
echo "════════════════════════════════════════════════════════════"
echo ""

PROJECT_DIR="/Users/kirillzaitsev/Documents/diplom/diploma-project"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для подтверждения
confirm() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Пожалуйста, ответьте y или n.";;
        esac
    done
}

echo "Этот скрипт удалит Docker контейнеры, образы и временные файлы."
echo ""

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Проект не найден в $PROJECT_DIR${NC}"
    exit 1
fi

# Резервная копия
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if confirm "Создать резервную копию проекта?"; then
    BACKUP_FILE="$HOME/Desktop/diploma-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    echo "Создаю архив..."
    tar -czf "$BACKUP_FILE" -C /Users/kirillzaitsev/Documents diplom/ 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Резервная копия создана: $BACKUP_FILE${NC}"
    else
        echo -e "${RED}✗ Ошибка создания резервной копии${NC}"
    fi
    echo ""
fi

# Остановка контейнеров
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if confirm "Остановить Docker контейнеры?"; then
    cd "$PROJECT_DIR"
    echo "Останавливаю контейнеры..."
    docker-compose down -v 2>/dev/null
    echo -e "${GREEN}✓ Контейнеры остановлены${NC}"
    echo ""
fi

# Удаление образов
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if confirm "Удалить Docker образы (~500-600 MB)?"; then
    echo "Удаляю Docker образы..."
    docker rmi diploma-project-ml-service diploma-project-web-service 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Docker образы удалены${NC}"
    else
        echo -e "${YELLOW}⚠ Образы уже удалены или не найдены${NC}"
    fi
    echo ""
fi

# Очистка временных файлов
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if confirm "Очистить временные файлы и кэш?"; then
    cd "$PROJECT_DIR"
    echo "Очищаю Python кэш..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete 2>/dev/null
    find . -type f -name "*.pyo" -delete 2>/dev/null
    find . -name ".DS_Store" -delete 2>/dev/null

    echo "Удаляю виртуальное окружение..."
    rm -rf ml-service/venv ml-service/.venv

    echo "Очищаю Go кэш..."
    cd web-service && go clean -cache -testcache 2>/dev/null && cd ..

    echo "Удаляю базу данных результатов..."
    rm -f data/results.db data/results.db-shm data/results.db-wal

    echo "Удаляю обученную модель..."
    rm -f data/model.pkl

    echo -e "${GREEN}✓ Временные файлы удалены${NC}"
    echo ""
fi

# Полное удаление проекта
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}⚠️  ВНИМАНИЕ: Следующий шаг удалит ВСЕ файлы проекта!${NC}"
if confirm "Удалить весь проект полностью?"; then
    echo "Удаляю проект..."
    cd /Users/kirillzaitsev/Documents
    rm -rf diplom
    echo -e "${GREEN}✓ Проект полностью удален${NC}"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo -e "${GREEN}  ✅ ПОЛНАЯ ОЧИСТКА ЗАВЕРШЕНА${NC}"
    echo "════════════════════════════════════════════════════════════"
    exit 0
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}  ✅ ОЧИСТКА ЗАВЕРШЕНА${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Освобождено места: ~500-600 MB"
echo "Проект сохранен в: $PROJECT_DIR"
echo ""
