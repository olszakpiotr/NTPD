
# Importujemy niezbędne biblioteki

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conlist
from typing import List
from pydantic import BaseModel, Field
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np


# Wczytanie zbioru danych Breast Cancer
data = load_breast_cancer()
X, y = data.data, data.target

# Podział na dane treningowe i testowe
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Trenowanie modelu - LogisticRegression
model = LogisticRegression(max_iter=10000)
model.fit(X_train, y_train)

# Ocena modelu
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Dokładność modelu na zbiorze testowym: {acc:.2f}")


app = FastAPI(title="API do serwowania modelu ML")

# Schemat danych wejściowych dla endpointu /predict
class PredictRequest(BaseModel):
    features: List[float] = Field(
        ..., 
        min_items=len(data.feature_names), 
        max_items=len(data.feature_names)
    )

# Endpoint główny
@app.get("/")
def read_root():
    return {"message": "Witamy w API serwującym model ML"}

# Endpoint predykcji
@app.post("/predict")
def predict(request: PredictRequest):
    try:
        # Konwersja danych wejściowych do macierzy NumPy
        input_data = np.array(request.features).reshape(1, -1)
        # Sprawdzenie, czy liczba cech jest poprawna
        if input_data.shape[1] != len(data.feature_names):
            raise HTTPException(status_code=400, detail=f"Oczekiwano {len(data.feature_names)} cech, otrzymano {input_data.shape[1]}")
        # Predykcja
        prediction = model.predict(input_data)[0]
        prediction_label = data.target_names[prediction]
        return {"prediction": int(prediction), "label": prediction_label}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint informacyjny o modelu
@app.get("/info")
def get_info():
    return {
        "model": "LogisticRegression",
        "n_features": len(data.feature_names),
        "feature_names": data.feature_names.tolist()
    }

# Endpoint sprawdzający stan serwera
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Komentarz: Aplikację można uruchomić komendą:
# uvicorn nazwa_pliku:app --host 0.0.0.0 --port 8000 --workers 4
