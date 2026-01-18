package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type SurveyRequest struct {
	Q1  int `json:"q1" binding:"required,min=1,max=5"`
	Q2  int `json:"q2" binding:"required,min=1,max=5"`
	Q3  int `json:"q3" binding:"required,min=1,max=5"`
	Q4  int `json:"q4" binding:"required,min=1,max=5"`
	Q5  int `json:"q5" binding:"required,min=1,max=5"`
	Q6  int `json:"q6" binding:"required,min=1,max=5"`
	Q7  int `json:"q7" binding:"required,min=1,max=5"`
	Q8  int `json:"q8" binding:"required,min=1,max=5"`
	Q9  int `json:"q9" binding:"required,min=1,max=5"`
	Q10 int `json:"q10" binding:"required,min=1,max=5"`
	Q11 int `json:"q11" binding:"required,min=1,max=5"`
	Q12 int `json:"q12" binding:"required,min=1,max=5"`
	Q13 int `json:"q13" binding:"required,min=1,max=5"`
	Q14 int `json:"q14" binding:"required,min=1,max=5"`
	Q15 int `json:"q15" binding:"required,min=1,max=5"`
	Q16 int `json:"q16" binding:"required,min=1,max=5"`
	Q17 int `json:"q17" binding:"required,min=1,max=5"`
	Q18 int `json:"q18" binding:"required,min=1,max=5"`
	Q19 int `json:"q19" binding:"required,min=1,max=5"`
	Q20 int `json:"q20" binding:"required,min=1,max=5"`
}

type SpecialtyResult struct {
	Speciality string  `json:"speciality"`
	Percentage float64 `json:"percentage"`
	Rank       int     `json:"rank"`
}

type PredictionResponse struct {
	Predictions map[string]float64 `json:"predictions"`
	Top5        []SpecialtyResult  `json:"top_5"`
}

type SubmitRequest struct {
	Name    string        `json:"name" binding:"required"`
	Email   string        `json:"email"`
	Answers SurveyRequest `json:"answers" binding:"required"`
}

var db *sql.DB
var mlServiceURL string

func main() {
	// Инициализация базы данных
	initDB()
	defer db.Close()

	// ML сервис URL
	mlServiceURL = os.Getenv("ML_SERVICE_URL")
	if mlServiceURL == "" {
		mlServiceURL = "http://localhost:8000"
	}

	// Настройка Gin
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// CORS
	r.Use(corsMiddleware())

	// Статические файлы
	r.Static("/static", "./static")
	r.LoadHTMLGlob("templates/*")

	// Маршруты
	r.GET("/", indexHandler)
	r.POST("/api/predict", predictHandler)
	r.POST("/api/submit", submitHandler)
	r.GET("/api/results/:id", resultsHandler)
	r.GET("/health", healthHandler)

	// Запуск сервера
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 Web Service запущен на порту %s", port)
	log.Printf("🔗 ML Service URL: %s", mlServiceURL)

	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Ошибка запуска сервера: %v", err)
	}
}

func initDB() {
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./data/results.db"
	}

	var err error
	db, err = sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Ошибка подключения к БД: %v", err)
	}

	// Создание таблицы
	createTableSQL := `
	CREATE TABLE IF NOT EXISTS survey_results (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		email TEXT,
		answers TEXT NOT NULL,
		predictions TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`

	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatalf("Ошибка создания таблицы: %v", err)
	}

	log.Println("✓ База данных инициализирована")
}

func corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

func indexHandler(c *gin.Context) {
	c.HTML(http.StatusOK, "index.html", gin.H{
		"title": "Процент профессионализма",
	})
}

func predictHandler(c *gin.Context) {
	var req SurveyRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректные данные: " + err.Error()})
		return
	}

	// Вызов ML сервиса
	predictions, err := callMLService(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка предсказания: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, predictions)
}

func submitHandler(c *gin.Context) {
	var req SubmitRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректные данные: " + err.Error()})
		return
	}

	// Получение предсказаний
	predictions, err := callMLService(req.Answers)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка предсказания: " + err.Error()})
		return
	}

	// Сохранение в БД
	answersJSON, _ := json.Marshal(req.Answers)
	predictionsJSON, _ := json.Marshal(predictions)

	result, err := db.Exec(
		"INSERT INTO survey_results (name, email, answers, predictions) VALUES (?, ?, ?, ?)",
		req.Name, req.Email, string(answersJSON), string(predictionsJSON),
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка сохранения результатов"})
		return
	}

	id, _ := result.LastInsertId()

	c.JSON(http.StatusOK, gin.H{
		"id":          id,
		"message":     "Результаты успешно сохранены",
		"predictions": predictions,
	})
}

func resultsHandler(c *gin.Context) {
	id := c.Param("id")

	var name, email, answers, predictions string
	var createdAt time.Time

	err := db.QueryRow(
		"SELECT name, email, answers, predictions, created_at FROM survey_results WHERE id = ?",
		id,
	).Scan(&name, &email, &answers, &predictions, &createdAt)

	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "Результаты не найдены"})
		return
	}
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка получения результатов"})
		return
	}

	var answersData SurveyRequest
	var predictionsData PredictionResponse
	json.Unmarshal([]byte(answers), &answersData)
	json.Unmarshal([]byte(predictions), &predictionsData)

	c.JSON(http.StatusOK, gin.H{
		"id":          id,
		"name":        name,
		"email":       email,
		"answers":     answersData,
		"predictions": predictionsData,
		"created_at":  createdAt,
	})
}

func healthHandler(c *gin.Context) {
	// Проверка БД
	err := db.Ping()
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"status": "unhealthy",
			"error":  "Database connection failed",
		})
		return
	}

	// Проверка ML сервиса
	resp, err := http.Get(mlServiceURL + "/health")
	mlHealthy := err == nil && resp.StatusCode == 200

	c.JSON(http.StatusOK, gin.H{
		"status":      "healthy",
		"database":    "connected",
		"ml_service":  mlHealthy,
		"timestamp":   time.Now(),
	})
}

func callMLService(req SurveyRequest) (*PredictionResponse, error) {
	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(
		mlServiceURL+"/predict",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("ML service error: %s", string(body))
	}

	var predictions PredictionResponse
	if err := json.NewDecoder(resp.Body).Decode(&predictions); err != nil {
		return nil, err
	}

	return &predictions, nil
}
