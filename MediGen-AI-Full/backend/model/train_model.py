"""
Trains a RandomForest classifier on the symptom-disease dataset
and saves the trained model + symptom list to disk using joblib.

Run:
    python train_model.py
"""
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "disease_model.pkl")
SYMPTOMS_PATH = os.path.join(BASE_DIR, "symptoms.pkl")


def main():
    df = pd.read_csv(DATASET_PATH)
    symptom_columns = [c for c in df.columns if c != "disease"]

    X = df[symptom_columns]
    y = df["disease"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=10, random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(symptom_columns, SYMPTOMS_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Symptom list saved to {SYMPTOMS_PATH}")


if __name__ == "__main__":
    main()
