# Руководство по развертыванию

## Содержание

1. [Локальное развертывание](#локальное-развертывание)
2. [Docker развертывание](#docker-развертывание)
3. [Production развертывание](#production-развертывание)
4. [Настройка CI/CD](#настройка-cicd)

---

## Локальное развертывание

### Требования

- Python 3.10+
- Go 1.21+
- SQLite3

### Шаг 1: Обучение модели

```bash
cd ml-service
python3 -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
```

### Шаг 2: Запуск ML Service

```bash
# В той же директории ml-service
uvicorn predict_api:app --reload --port 8000
```

ML Service будет доступен на http://localhost:8000

### Шаг 3: Запуск Web Service

Откройте новый терминал:

```bash
cd web-service
go mod download
export ML_SERVICE_URL=http://localhost:8000
go run main.go
```

Web Service будет доступен на http://localhost:8080

---

## Docker развертывание

### Требования

- Docker 20.10+
- Docker Compose 1.29+

### Быстрый старт

```bash
# Клонирование репозитория
git clone <repository-url>
cd diploma-project

# Обучение модели (первый запуск)
cd ml-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_model.py
cd ..

# Запуск всех сервисов
docker-compose up -d
```

### Проверка статуса

```bash
# Просмотр логов
docker-compose logs -f

# Проверка контейнеров
docker-compose ps

# Health check
curl http://localhost:8080/health
curl http://localhost:8000/health
```

### Остановка сервисов

```bash
docker-compose down
```

### Перезапуск с очисткой

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## Production развертывание

### Вариант 1: VPS/Dedicated Server

#### Требования

- Ubuntu 20.04+ / Debian 11+
- Минимум 2GB RAM
- Docker и Docker Compose

#### Установка Docker

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose -y

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

#### Развертывание

```bash
# Клонирование проекта
git clone <repository-url>
cd diploma-project

# Обучение модели
cd ml-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_model.py
cd ..

# Запуск сервисов
docker-compose up -d

# Настройка автозапуска
sudo systemctl enable docker
```

#### Настройка Nginx (опционально)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### SSL с Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Вариант 2: Cloud платформы

#### Heroku

```bash
# Установка Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Логин
heroku login

# Создание приложения
heroku create diploma-project-app

# Деплой
git push heroku main
```

#### Render.com

1. Создайте новый Web Service в Render.com
2. Подключите GitHub репозиторий
3. Настройте:
   - Build Command: `docker-compose build`
   - Start Command: `docker-compose up`

#### AWS (EC2)

```bash
# Подключение к EC2
ssh -i your-key.pem ubuntu@ec2-instance-ip

# Установка Docker
sudo apt update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Клонирование и запуск
git clone <repository-url>
cd diploma-project
docker-compose up -d
```

---

## Настройка CI/CD

### GitHub Actions

Файл уже создан в `.github/workflows/ci-cd.yml`

#### Настройка secrets

В настройках GitHub репозитория добавьте:

1. `DOCKER_USERNAME` - ваш username на Docker Hub
2. `DOCKER_PASSWORD` - пароль или access token Docker Hub

#### Процесс CI/CD

1. **Push в ветку develop** - запуск тестов
2. **Push в ветку main** - тесты + сборка + деплой
3. **Pull Request** - автоматическое тестирование

### Ручной деплой

```bash
# Сборка образов
docker build -t your-username/diploma-ml-service:latest ./ml-service
docker build -t your-username/diploma-web-service:latest ./web-service

# Push в Docker Hub
docker push your-username/diploma-ml-service:latest
docker push your-username/diploma-web-service:latest

# На production сервере
docker pull your-username/diploma-ml-service:latest
docker pull your-username/diploma-web-service:latest
docker-compose up -d
```

---

## Переменные окружения

### ML Service

```env
MODEL_PATH=/app/data/model.pkl
```

### Web Service

```env
ML_SERVICE_URL=http://ml-service:8000
PORT=8080
DB_PATH=/app/data/results.db
```

### Docker Compose override (production)

Создайте `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web-service:
    environment:
      - GIN_MODE=release
    restart: always

  ml-service:
    environment:
      - WORKERS=4
    restart: always
```

Запуск:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Мониторинг

### Проверка здоровья сервисов

```bash
# Web Service
curl http://localhost:8080/health

# ML Service
curl http://localhost:8000/health
```

### Логи

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f web-service
docker-compose logs -f ml-service
```

### Метрики

Для production рекомендуется:

- **Prometheus** - сбор метрик
- **Grafana** - визуализация
- **Loki** - агрегация логов

---

## Резервное копирование

### База данных

```bash
# Бэкап
docker exec web-service sqlite3 /app/data/results.db ".backup '/app/data/backup.db'"

# Копирование бэкапа
docker cp web-service:/app/data/backup.db ./backup-$(date +%Y%m%d).db
```

### Модель

```bash
# Копирование модели
docker cp ml-service:/app/data/model.pkl ./model-backup.pkl
```

---

## Обновление

### Обновление кода

```bash
git pull origin main
docker-compose build
docker-compose up -d
```

### Обновление модели

```bash
# Обучение новой модели
cd ml-service
source venv/bin/activate
python train_model.py

# Рестарт ML сервиса
docker-compose restart ml-service
```

---

## Troubleshooting

### ML Service не запускается

```bash
# Проверка логов
docker-compose logs ml-service

# Проверка наличия модели
ls -lh data/model.pkl

# Переобучение модели
cd ml-service
python train_model.py
```

### Web Service не может подключиться к ML Service

```bash
# Проверка сети
docker network ls
docker network inspect diploma-network

# Проверка переменных окружения
docker exec web-service env | grep ML_SERVICE_URL
```

### База данных заблокирована

```bash
# Остановка сервисов
docker-compose down

# Очистка lock файлов
rm -f data/*.db-shm data/*.db-wal

# Перезапуск
docker-compose up -d
```

---

## Контакты и поддержка

Для вопросов и багрепортов используйте GitHub Issues.
