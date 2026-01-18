from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import joblib
import numpy as np
import os
from typing import List, Dict, Any

app = FastAPI(title="ML Prediction Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальная переменная для модели
model_data = None

class PredictionRequest(BaseModel):
    q1: int
    q2: int
    q3: int
    q4: int
    q5: int
    q6: int
    q7: int
    q8: int
    q9: int
    q10: int
    q11: int
    q12: int
    q13: int
    q14: int
    q15: int
    q16: int
    q17: int
    q18: int
    q19: int
    q20: int

    @validator('*')
    def check_range(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Значение должно быть от 1 до 5')
        return v

class PredictionResponse(BaseModel):
    predictions: Dict[str, float]
    top_5: List[Dict[str, Any]]

def load_model():
    """Загрузка обученной модели"""
    global model_data

    model_path = os.environ.get('MODEL_PATH', '/app/data/model.pkl')

    # Альтернативные пути
    if not os.path.exists(model_path):
        model_path = '../data/model.pkl'
    if not os.path.exists(model_path):
        model_path = 'data/model.pkl'

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Модель не найдена: {model_path}")

    model_data = joblib.load(model_path)
    print(f"✓ Модель загружена из {model_path}")
    print(f"✓ Точность модели: {model_data['accuracy']:.4f}")
    print(f"✓ Количество классов: {len(model_data['label_encoder'].classes_)}")

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    try:
        load_model()
    except Exception as e:
        print(f"⚠ Предупреждение: Модель не загружена - {e}")
        print("  Запустите train_model.py для создания модели")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "ML Prediction Service",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": model_data is not None
    }

@app.get("/health")
async def health():
    """Проверка работоспособности"""
    if model_data is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")

    return {
        "status": "healthy",
        "model_accuracy": float(model_data['accuracy']),
        "classes_count": len(model_data['label_encoder'].classes_)
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Предсказание специальностей"""
    if model_data is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")

    try:
        # Подготовка входных данных
        features = np.array([[
            request.q1, request.q2, request.q3, request.q4, request.q5,
            request.q6, request.q7, request.q8, request.q9, request.q10,
            request.q11, request.q12, request.q13, request.q14, request.q15,
            request.q16, request.q17, request.q18, request.q19, request.q20
        ]])

        # Получение вероятностей
        probabilities = model_data['model'].predict_proba(features)[0]
        classes = model_data['label_encoder'].classes_

        # Формирование результата
        predictions = {}
        for class_name, prob in zip(classes, probabilities):
            predictions[class_name] = round(float(prob * 100), 2)

        # Топ-5 специальностей
        sorted_predictions = sorted(
            predictions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_5 = [
            {
                "speciality": spec,
                "percentage": perc,
                "rank": idx + 1
            }
            for idx, (spec, perc) in enumerate(sorted_predictions[:5])
        ]

        return PredictionResponse(
            predictions=predictions,
            top_5=top_5
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {str(e)}")

@app.get("/specialties")
async def get_specialties():
    """Получить список всех специальностей"""
    if model_data is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")

    return {
        "specialties": model_data['label_encoder'].classes_.tolist(),
        "count": len(model_data['label_encoder'].classes_)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
