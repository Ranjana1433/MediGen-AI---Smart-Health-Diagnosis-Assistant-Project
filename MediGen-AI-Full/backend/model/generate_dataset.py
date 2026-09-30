"""
Generates a synthetic symptom-disease dataset for training the ML model.
Run this once to (re)create dataset.csv before training.
"""
import csv
import random

random.seed(42)

SYMPTOMS = [
    "fever", "cough", "fatigue", "headache", "sore_throat",
    "shortness_of_breath", "chest_pain", "nausea", "vomiting", "diarrhea",
    "body_ache", "chills", "runny_nose", "loss_of_taste", "loss_of_smell",
    "dizziness", "rash", "joint_pain", "abdominal_pain", "high_blood_pressure"
]

# Core symptom profile per disease (symptoms that are commonly present)
DISEASE_PROFILES = {
    "Common Cold": ["cough", "runny_nose", "sore_throat", "headache", "fatigue"],
    "Influenza (Flu)": ["fever", "body_ache", "chills", "cough", "headache", "fatigue"],
    "COVID-19": ["fever", "cough", "fatigue", "loss_of_taste", "loss_of_smell", "shortness_of_breath"],
    "Migraine": ["headache", "dizziness", "nausea", "fatigue"],
    "Food Poisoning": ["nausea", "vomiting", "diarrhea", "abdominal_pain", "fever"],
    "Malaria": ["fever", "chills", "body_ache", "headache", "fatigue"],
    "Typhoid": ["fever", "abdominal_pain", "headache", "fatigue", "body_ache"],
    "Dengue": ["fever", "rash", "joint_pain", "headache", "body_ache"],
    "Hypertension": ["headache", "dizziness", "chest_pain", "high_blood_pressure"],
    "Gastritis": ["abdominal_pain", "nausea", "vomiting", "fatigue"],
}

ROWS_PER_DISEASE = 40


def generate_row(core_symptoms):
    row = {s: 0 for s in SYMPTOMS}
    # include most core symptoms (randomly drop 0-1 for variability)
    drop_count = random.choice([0, 0, 1])
    symptoms_present = core_symptoms.copy()
    if drop_count and len(symptoms_present) > 2:
        symptoms_present.pop(random.randrange(len(symptoms_present)))
    for s in symptoms_present:
        row[s] = 1
    # occasionally add 1 random noisy symptom not in the core list
    if random.random() < 0.25:
        noise = random.choice([s for s in SYMPTOMS if s not in core_symptoms])
        row[noise] = 1
    return row


def main():
    out_path = "dataset.csv"
    fieldnames = SYMPTOMS + ["disease"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for disease, core_symptoms in DISEASE_PROFILES.items():
            for _ in range(ROWS_PER_DISEASE):
                row = generate_row(core_symptoms)
                row["disease"] = disease
                writer.writerow(row)
    print(f"Dataset written to {out_path}")


if __name__ == "__main__":
    main()
