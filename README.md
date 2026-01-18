# Дипломный проект "Процент профессионализма"

Система ML-рекомендаций специальностей колледжа.

## Быстрый старт

```bash
cd diploma-project
./setup.sh
docker-compose up -d
```

Веб-интерфейс: http://localhost:8080

## Документация

Вся документация находится в папке `diploma-project/`:

- **README.md** - Полное руководство по проекту
- **QUICK_START.md** - Краткое руководство для быстрого старта
- **PRESENTATION.md** - Презентация для защиты диплома
- **CHANGELOG.md** - История изменений
- **docs/** - Техническая документация

## Структура

```
diplom/
└── diploma-project/     # Основной проект
    ├── README.md        # Начните здесь
    ├── ml-service/      # Python ML сервис
    ├── web-service/     # Go веб-сервис
    ├── data/            # Датасет
    └── docs/            # Документация
```

## Первый запуск

1. Перейдите в директорию проекта:
   ```bash
   cd diploma-project
   ```

2. Обучите ML модель:
   ```bash
   cd ml-service
   pip3 install pandas scikit-learn joblib
   python3 train_simple.py
   cd ..
   ```

3. Запустите Docker контейнеры:
   ```bash
   docker-compose up --build -d
   ```

4. Откройте браузер:
   ```
   http://localhost:8080
   ```

## Требования

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.8+ (для обучения модели)

---

Подробная инструкция в **diploma-project/README.md**
