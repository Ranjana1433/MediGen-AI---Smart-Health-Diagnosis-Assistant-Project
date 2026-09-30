"""
MediGen AI — Smart Health Diagnosis Assistant (FastAPI backend)
Run with:
    uvicorn main:app --reload
Then open http://127.0.0.1:8000 in your browser — you'll land on the
login page first, then the symptom-checker dashboard after signing in.
"""
import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from model.disease_info import get_disease_info, MEDICAL_DISCLAIMER
from model.doctors import DOCTORS, get_doctors_by_specialty, get_doctor_by_id
from genai.generative_assistant import generate_explanation
import database
import auth

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "disease_model.pkl")
SYMPTOMS_PATH = os.path.join(BASE_DIR, "model", "symptoms.pkl")
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = FastAPI(
    title="MediGen AI — Smart Health Diagnosis Assistant API",
    description="ML + Generative AI powered preliminary health diagnosis assistant with login, voice input, appointment booking, and analytics charts.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model + symptom list at startup

import sys
sys.path.insert(0, os.path.join(BASE_DIR, "model"))
try:
    # Always train fresh on THIS computer so the model matches your Python/scikit-learn version.
    import train_model
    train_model.main()
except Exception as e:
    print("Retrain skipped:", e)
model = joblib.load(MODEL_PATH)
SYMPTOM_LIST: List[str] = joblib.load(SYMPTOMS_PATH)

database.init_db()
auth.init_auth_db()


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = Field(default="user", description="'user' or 'admin'")


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/register")
def register(request: RegisterRequest):
    success, message = auth.register_user(request.email, request.password, request.role)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.post("/api/login")
def login(request: LoginRequest):
    success, result = auth.verify_login(request.email, request.password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
    session = auth.get_session(result)
    return {"token": result, "email": session["email"], "role": session["role"]}


@app.post("/api/logout")
def logout(token: str):
    auth.logout(token)
    return {"message": "Logged out."}


@app.get("/api/me")
def me(token: str):
    session = auth.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return session


def require_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """Resolves the logged-in {'email', 'role'} from the 'Authorization: Bearer <token>' header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    token = authorization.removeprefix("Bearer ").strip()
    session = auth.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    return session


class DiagnosisRequest(BaseModel):
    name: Optional[str] = Field(default="Guest", description="User's name")
    symptoms: List[str] = Field(
        ..., description="List of symptom keys, e.g. ['fever', 'cough']"
    )


class DiagnosisResponse(BaseModel):
    predicted_disease: str
    confidence: float
    severity: str
    specialist: str
    precautions: List[str]
    medicines: List[str]
    medical_disclaimer: str
    explanation: str
    top_predictions: List[dict]


@app.get("/api/symptoms")
def list_symptoms():
    """Returns the list of symptoms the model understands, for building the UI."""
    return {"symptoms": SYMPTOM_LIST}


@app.post("/api/diagnose", response_model=DiagnosisResponse)
def diagnose(request: DiagnosisRequest, current_user: dict = Depends(require_user)):
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="Please provide at least one symptom.")

    unknown = [s for s in request.symptoms if s not in SYMPTOM_LIST]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown symptom(s): {unknown}. Call /api/symptoms for valid options.",
        )

    # Build feature vector (as a DataFrame so column names match training data)
    input_vector = [1 if s in request.symptoms else 0 for s in SYMPTOM_LIST]
    input_df = pd.DataFrame([input_vector], columns=SYMPTOM_LIST)

    try:
        probabilities = model.predict_proba(input_df)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {e}")
    classes = model.classes_

    # Rank predictions
    ranked = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
    top_disease, top_prob = ranked[0]
    confidence = round(float(top_prob) * 100, 2)

    top_predictions = [
        {"disease": d, "confidence": round(float(p) * 100, 2)} for d, p in ranked[:3]
    ]

    info = get_disease_info(top_disease)
    severity = info["severity"]
    specialist = info["specialist"]
    precautions = info["precautions"]
    medicines = info["medicines"]

    try:
        explanation = generate_explanation(
            disease=top_disease,
            confidence=confidence,
            symptoms=request.symptoms,
            severity=severity,
            precautions=precautions,
            medicines=medicines,
        )
    except Exception:
        explanation = (f"Based on your symptoms, the most likely condition is {top_disease} "
                       f"({confidence}% confidence). Please follow the precautions and consult a doctor.")

    database.save_record(
        username=current_user["email"],
        name=request.name,
        symptoms=request.symptoms,
        disease=top_disease,
        confidence=confidence,
        severity=severity,
        explanation=explanation,
    )

    return DiagnosisResponse(
        predicted_disease=top_disease,
        confidence=confidence,
        severity=severity,
        specialist=specialist,
        precautions=precautions,
        medicines=medicines,
        medical_disclaimer=MEDICAL_DISCLAIMER,
        explanation=explanation,
        top_predictions=top_predictions,
    )


@app.get("/api/history")
def history(limit: int = 20, current_user: dict = Depends(require_user)):
    # Admins see every user's checks; regular users see only their own.
    if current_user["role"] == "admin":
        return {"history": database.get_history(username=None, limit=limit)}
    return {"history": database.get_history(username=current_user["email"], limit=limit)}


# ---------------- Appointments ----------------

class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., description="Name of the patient")
    doctor_id: str = Field(..., description="Doctor id from /api/doctors")
    appointment_date: str = Field(..., description="YYYY-MM-DD")
    appointment_time: str = Field(..., description="e.g. '10:00 AM'")
    reason: Optional[str] = Field(default="", description="Reason / symptoms for the visit")


@app.get("/api/doctors")
def list_doctors(specialty: Optional[str] = None):
    """Returns the doctor roster, optionally filtered by specialty."""
    if specialty:
        return {"doctors": get_doctors_by_specialty(specialty)}
    return {"doctors": DOCTORS}


@app.post("/api/appointments")
def book_appointment(request: AppointmentRequest, current_user: dict = Depends(require_user)):
    doctor = get_doctor_by_id(request.doctor_id)
    if not doctor:
        raise HTTPException(status_code=400, detail="Selected doctor was not found.")

    if not request.patient_name.strip():
        raise HTTPException(status_code=400, detail="Patient name is required.")
    if not request.appointment_date or not request.appointment_time:
        raise HTTPException(status_code=400, detail="Please select both a date and a time slot.")
    if request.appointment_time not in doctor["available_slots"]:
        raise HTTPException(
            status_code=400,
            detail=f"That time slot isn't available for {doctor['name']}. "
                   f"Available slots: {', '.join(doctor['available_slots'])}",
        )

    appointment_id = database.save_appointment(
        username=current_user["email"],
        patient_name=request.patient_name.strip(),
        doctor_id=doctor["id"],
        doctor_name=doctor["name"],
        specialty=doctor["specialty"],
        appointment_date=request.appointment_date,
        appointment_time=request.appointment_time,
        reason=request.reason or "",
    )

    return {
        "message": f"Appointment booked with {doctor['name']} ({doctor['specialty']}) "
                   f"on {request.appointment_date} at {request.appointment_time}.",
        "appointment_id": appointment_id,
    }


@app.get("/api/appointments")
def my_appointments(current_user: dict = Depends(require_user)):
    # Admins see every user's appointments; regular users see only their own.
    if current_user["role"] == "admin":
        return {"appointments": database.get_appointments(username=None)}
    return {"appointments": database.get_appointments(username=current_user["email"])}


@app.delete("/api/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, current_user: dict = Depends(require_user)):
    cancelled = database.cancel_appointment(appointment_id, current_user["email"])
    if not cancelled:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found, or you don't have permission to cancel it.",
        )
    return {"message": "Appointment cancelled."}


# ---------------- Admin ----------------

def require_admin(current_user: dict = Depends(require_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access only.")
    return current_user


@app.get("/api/admin/stats")
def admin_stats(_: dict = Depends(require_admin)):
    users = auth.list_users()
    hist = database.get_history(username=None, limit=100000)
    counts = {}
    for h in hist:
        d = h.get("predicted_disease") or "Unknown"
        counts[d] = counts.get(d, 0) + 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:6]
    return {
        "users": sum(1 for u in users if u["role"] == "user"),
        "admins": sum(1 for u in users if u["role"] == "admin"),
        "diagnoses": len(hist),
        "appointments": len(database.get_appointments(username=None)),
        "top_diseases": [{"disease": k, "count": v} for k, v in top],
    }


@app.get("/api/admin/users")
def admin_users(_: dict = Depends(require_admin)):
    return {"users": auth.list_users()}


@app.delete("/api/admin/users")
def admin_delete_user(email: str, _: dict = Depends(require_admin)):
    if not auth.delete_user(email):
        raise HTTPException(status_code=400, detail="User not found or cannot be deleted.")
    return {"message": "User deleted."}


# Serve the frontend (so the whole app can run from a single FastAPI server)
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        return FileResponse(index_path)

    @app.get("/login")
    def serve_login():
        login_path = os.path.join(FRONTEND_DIR, "login.html")
        return FileResponse(login_path)


if __name__ == "__main__":
    import threading, webbrowser, uvicorn
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
