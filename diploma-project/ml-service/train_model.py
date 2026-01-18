import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

def train_model():
    print("=" * 80)
    print("ОБУЧЕНИЕ МОДЕЛИ ПРОФОРИЕНТАЦИИ")
    print("=" * 80)

    # Загрузка данных
    print("\n[1/6] Загрузка данных...")
    data_path = '../data/survey_data.csv'
    if not os.path.exists(data_path):
        data_path = 'data/survey_data.csv'

    df = pd.read_csv(data_path)
    print(f"✓ Загружено записей: {len(df)}")
    print(f"✓ Количество специальностей: {df['speciality'].nunique()}")

    # Подготовка данных
    print("\n[2/6] Подготовка данных...")
    X = df.iloc[:, 2:22].values  # 20 вопросов (колонки 2-21)
    y = df['speciality'].values

    # Кодирование специальностей
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    print(f"✓ Признаков: {X.shape[1]}")
    print(f"✓ Классов: {len(label_encoder.classes_)}")

    # Разделение на train/test
    print("\n[3/6] Разделение на обучающую и тестовую выборки...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"✓ Обучающая выборка: {len(X_train)}")
    print(f"✓ Тестовая выборка: {len(X_test)}")

    # Обучение модели
    print("\n[4/6] Обучение модели Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("✓ Модель обучена")

    # Кросс-валидация
    print("\n[5/6] Кросс-валидация (5-fold)...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"✓ Средняя точность CV: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Оценка на тестовой выборке
    print("\n[6/6] Оценка на тестовой выборке...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✓ Точность на тесте: {accuracy:.4f} ({accuracy*100:.2f}%)")

    # Детальный отчет
    print("\n" + "=" * 80)
    print("МЕТРИКИ КЛАССИФИКАЦИИ")
    print("=" * 80)
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    ))

    # Важность признаков
    print("\n" + "=" * 80)
    print("ВАЖНОСТЬ ПРИЗНАКОВ (TOP-10)")
    print("=" * 80)
    feature_importance = pd.DataFrame({
        'Вопрос': [f'q{i+1}' for i in range(20)],
        'Важность': model.feature_importances_
    }).sort_values('Важность', ascending=False)

    print(feature_importance.head(10).to_string(index=False))

    # Сохранение модели
    print("\n" + "=" * 80)
    print("СОХРАНЕНИЕ МОДЕЛИ")
    print("=" * 80)

    model_data = {
        'model': model,
        'label_encoder': label_encoder,
        'feature_names': [f'q{i+1}' for i in range(20)],
        'accuracy': accuracy,
        'cv_scores': cv_scores
    }

    model_path = '../data/model.pkl'
    if not os.path.exists('../data'):
        model_path = 'data/model.pkl'
        os.makedirs('data', exist_ok=True)

    joblib.dump(model_data, model_path)
    print(f"✓ Модель сохранена: {model_path}")
    print(f"✓ Размер файла: {os.path.getsize(model_path) / 1024:.2f} KB")

    print("\n" + "=" * 80)
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("=" * 80)

    return model_data

if __name__ == "__main__":
    train_model()
