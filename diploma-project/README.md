# Процент профессионализма

Система ML-рекомендаций специальностей колледжа на основе профориентационного теста.

## Описание

Веб-приложение для определения соответствия абитуриента специальностям колледжа по результатам опроса из 20 вопросов. Система использует машинное обучение (Random Forest) для расчета процента профессионализма по 27 направлениям подготовки.

**27 специальностей:**
Программирование, Информационная безопасность, Веб-разработка, Системное администрирование, DevOps, Мобильная разработка, Data Science, GameDev, Дизайн, 3D-моделирование, Анимация, Графический дизайн, UX/UI дизайн, Видеомонтаж, Фотография, Маркетинг, PR, Медиапроизводство, Журналистика, Бухгалтерия, Банковское дело, Финансы, Страхование, Строительство, Архитектура, Электротехника, Автоматизация.

## Технологический стек

- **Frontend**: HTML5, Bootstrap 5, JavaScript, Яндекс.Формы (iframe)
- **Backend**: Go (Gin framework), SQLite
- **ML Service**: Python, FastAPI, scikit-learn, pandas, joblib
- **DevOps**: Docker, Docker Compose

## Быстрый старт

### Требования

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.8+ (для обучения модели)

### Первый запуск

**Шаг 1: Обучение модели**

Перед запуском Docker-контейнеров необходимо обучить ML модель:

```bash
cd diploma-project/ml-service
pip3 install pandas scikit-learn joblib
python3 train_simple.py
```

Модель будет сохранена в `data/model.pkl`. Ожидаемая точность: ~71%.

**Шаг 2: Запуск сервисов**

```bash
cd diploma-project
docker-compose up --build -d
```

**Шаг 3: Проверка**

```bash
# Проверка статуса контейнеров
docker ps

# Проверка здоровья сервисов
curl http://localhost:8080/health
curl http://localhost:8000/health
```

Приложение доступно по адресу: **http://localhost:8080**

### Быстрый старт (автоматический)

Или используйте автоматический скрипт:

```bash
cd diploma-project
./setup.sh
docker-compose up -d
```

### Остановка

```bash
docker-compose down
```

### Полная очистка

```bash
docker-compose down -v
docker rmi diploma-project-ml-service diploma-project-web-service
```

## Архитектура

```
┌─────────────────┐
│  Яндекс.Форма   │
│  (20 вопросов)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Go Web Service │─────▶│  ML Service      │
│  (Gin, SQLite)  │      │  (FastAPI)       │
│  Port: 8080     │◀─────│  Port: 8000      │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐
│   SQLite DB     │
│  (results.db)   │
└─────────────────┘
```

## Структура проекта

```
diploma-project/
├── README.md              # Этот файл
├── QUICK_START.md         # Краткое руководство
├── PRESENTATION.md        # Презентация проекта
├── CHANGELOG.md           # История изменений
├── docker-compose.yml     # Docker Compose конфигурация
├── Makefile               # Команды для сборки
├── setup.sh               # Автоматический скрипт установки
│
├── data/                  # Данные
│   └── survey_data.csv    # Датасет для обучения (540 записей)
│
├── ml-service/            # Python ML сервис
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── predict_api.py     # FastAPI приложение
│   ├── train_model.py     # Обучение модели
│   └── train_simple.py    # Упрощенная версия обучения
│
├── web-service/           # Go веб-сервис
│   ├── Dockerfile
│   ├── main.go            # Главный файл приложения
│   ├── go.mod
│   ├── go.sum
│   ├── templates/         # HTML шаблоны
│   │   └── index.html
│   └── static/            # Статические файлы
│
└── docs/                  # Техническая документация
    ├── architecture.md    # Архитектура системы
    ├── deployment.md      # Руководство по развертыванию
    └── model_report.md    # Отчет о ML модели
```

## API Endpoints

### Web Service (Go) - Port 8080

- `GET /` - Главная страница с формой
- `POST /api/predict` - Получение рекомендаций по специальностям
- `POST /api/submit` - Сохранение результатов теста
- `GET /api/results/:id` - Просмотр результатов теста
- `GET /health` - Проверка работоспособности

### ML Service (Python) - Port 8000

- `POST /predict` - Предсказание вероятностей по специальностям
- `GET /health` - Проверка работоспособности
- `GET /specialties` - Список всех специальностей
- `GET /` - Информация о сервисе

## Разработка

### Локальная разработка ML сервиса

```bash
cd ml-service
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
uvicorn predict_api:app --reload --port 8000
```

### Локальная разработка Web сервиса

```bash
cd web-service
go mod download
go run main.go
```

## Обучение модели

### Полная версия

```bash
cd ml-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_model.py
```

### Упрощенная версия (рекомендуется)

```bash
cd ml-service
pip3 install pandas scikit-learn joblib
python3 train_simple.py
```

Модель сохраняется в `data/model.pkl`. Параметры модели:
- Алгоритм: Random Forest Classifier
- Количество деревьев: 200
- Максимальная глубина: 20
- Количество классов: 27
- Ожидаемая точность: ~71%

## Решение проблем

### ML сервис не запускается

```bash
# Проверьте наличие модели
ls -lh data/model.pkl

# Если модели нет, обучите её
cd ml-service
python3 train_simple.py

# Перезапустите контейнер
docker-compose restart ml-service
```

### Ошибки при сборке Docker

```bash
# Полная очистка и пересборка
docker-compose down -v
docker system prune -f
docker-compose up --build -d
```

### Порты заняты

```bash
# Проверьте какие процессы используют порты
lsof -i :8080
lsof -i :8000

# Остановите конфликтующие процессы или измените порты в docker-compose.yml
```

### Ошибка SQLite в Alpine Linux

Если используется Alpine Linux, возникают ошибки компиляции SQLite. Решение уже применено в Dockerfile - используется Debian-based образ.

## Тестирование

### ML сервис

```bash
cd ml-service
pytest tests/
```

### Web сервис

```bash
cd web-service
go test ./...
```

### Ручное тестирование API

```bash
# Проверка ML сервиса
curl http://localhost:8000/health

# Тестовый запрос предсказания
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"q1":5,"q2":5,"q3":4,"q4":5,"q5":3,"q6":2,"q7":2,"q8":3,"q9":2,"q10":1,"q11":5,"q12":4,"q13":5,"q14":3,"q15":2,"q16":3,"q17":2,"q18":3,"q19":5,"q20":4}'
```

## Команды Makefile

```bash
make build    # Сборка Docker образов
make up       # Запуск контейнеров
make down     # Остановка контейнеров
make logs     # Просмотр логов
make clean    # Очистка временных файлов
make restart  # Перезапуск сервисов
```

## Документация

- [QUICK_START.md](QUICK_START.md) - Быстрый старт для новых пользователей
- [PRESENTATION.md](PRESENTATION.md) - Презентация проекта для защиты диплома
- [CHANGELOG.md](CHANGELOG.md) - История изменений
- [docs/architecture.md](docs/architecture.md) - Детальная архитектура системы
- [docs/deployment.md](docs/deployment.md) - Руководство по развертыванию в production
- [docs/model_report.md](docs/model_report.md) - Отчет о ML модели и метриках

## Системные требования

### Для разработки
- OS: macOS, Linux, Windows 10+
- RAM: 4 GB минимум, 8 GB рекомендуется
- Disk: 2 GB свободного места
- Docker: 20.10+
- Python: 3.8+
- Go: 1.21+

### Для production
- RAM: 2 GB минимум
- CPU: 2 cores рекомендуется
- Disk: 1 GB

## Авторы

Дипломный проект "Процент профессионализма"

---

**Статус проекта:** ✅ Готов к использованию

**Последнее обновление:** 2026-01-18
