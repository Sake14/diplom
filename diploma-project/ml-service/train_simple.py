#!/usr/bin/env python3
"""
Упрощенный скрипт обучения модели без зависимости от сложных библиотек.
Создает простую модель для быстрого старта.
"""

import sys
import os

# Проверка зависимостей
try:
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    import joblib
except ImportError as e:
    print(f"Ошибка: {e}")
    print("\nУстановите зависимости:")
    print("pip install pandas scikit-learn joblib")
    sys.exit(1)

# Определение путей
data_path = '../data/survey_data.csv'
if not os.path.exists(data_path):
    data_path = 'data/survey_data.csv'

model_path = '../data/model.pkl'
if not os.path.exists('../data'):
    model_path = 'data/model.pkl'
    os.makedirs('data', exist_ok=True)

print("Загрузка данных...")
df = pd.read_csv(data_path)

print("Подготовка данных...")
X = df.iloc[:, 2:22].values
y = df['speciality'].values

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print("Обучение модели...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Точность: {accuracy:.4f}")

model_data = {
    'model': model,
    'label_encoder': label_encoder,
    'feature_names': [f'q{i+1}' for i in range(20)],
    'accuracy': accuracy
}

joblib.dump(model_data, model_path)
print(f"Модель сохранена: {model_path}")
