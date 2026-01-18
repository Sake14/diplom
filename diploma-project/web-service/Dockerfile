FROM golang:1.21 AS builder

WORKDIR /build

# Копирование go mod files
COPY go.mod go.sum ./
RUN go mod download

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN CGO_ENABLED=1 go build -o main .

# Финальный образ
FROM debian:bookworm-slim

WORKDIR /app

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

# Копирование бинарника
COPY --from=builder /build/main .

# Копирование templates и static
COPY templates ./templates
COPY static ./static

# Создание директории для данных
RUN mkdir -p /app/data

# Открытие порта
EXPOSE 8080

# Запуск приложения
CMD ["./main"]
