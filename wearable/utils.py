import joblib
import numpy as np

def predict_mood(heart_rate, steps, sleep_hours):
    model = joblib.load('mood_predictor.pkl')
    features = np.array([[heart_rate, steps, sleep_hours]])
    predicted_score = model.predict(features)[0]
    return round(predicted_score, 2)
