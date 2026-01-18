#!/bin/bash

# Легкая очистка - удаляет временные файлы, но сохраняет код

echo "════════════════════════════════════════════════════════════"
echo "  🧹 ЛЕГКАЯ ОЧИСТКА (код сохраняется, временные файлы удаляются)"
echo "════════════════════════════════════════════════════════════"
echo ""

PROJECT_DIR="/Users/kirillzaitsev/Documents/diplom/diploma-project"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Проект не найден в $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo "📁 Останавливаю Docker контейнеры..."
docker-compose down -v 2>/dev/null
echo "✓ Готово"
echo ""

echo "🧹 Очищаю Python кэш..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
echo "✓ Готово"
echo ""

echo "📋 Удаляю логи..."
find . -type f -name "*.log" -delete 2>/dev/null
echo "✓ Готово"
echo ""

echo "🐍 Удаляю виртуальное окружение (~500MB)..."
rm -rf ml-service/venv
echo "✓ Готово"
echo ""

echo "💾 Очищаю базу данных результатов..."
rm -f data/results.db*
echo "✓ Готово"
echo ""

echo "🗑️  Очищаю Go кэш..."
cd web-service
go clean -cache -modcache -testcache 2>/dev/null
cd ..
echo "✓ Готово"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  ✅ ЛЕГКАЯ ОЧИСТКА ЗАВЕРШЕНА"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Удалено:"
echo "  ✓ Временные файлы и кэш"
echo "  ✓ Python виртуальное окружение"
echo "  ✓ База данных результатов"
echo "  ✓ Логи"
echo ""
echo "Сохранено:"
echo "  ✓ Исходный код"
echo "  ✓ Документация"
echo "  ✓ Датасет и обученная модель"
echo ""
echo "📊 Освобождено: ~500-600 MB"
echo ""
echo "Проект сохранен в: $PROJECT_DIR"
echo ""
echo "Для полного удаления используйте: ./cleanup.sh"
echo ""
