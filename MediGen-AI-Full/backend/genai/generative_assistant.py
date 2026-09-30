"""
Generative AI layer.

If an OPENAI_API_KEY is present in the environment, this module calls
OpenAI's Chat Completions API to turn the raw ML prediction into a
natural, human-friendly explanation (this is the "Generative AI" part
of the project).

If no API key is configured, it falls back to a rule-based template
generator so the whole app still runs end-to-end out of the box
without requiring anyone to pay for an API key.
"""
import os

try:
    from openai import OpenAI
    _OPENAI_SDK_AVAILABLE = True
except ImportError:
    _OPENAI_SDK_AVAILABLE = False


def _template_fallback(disease, confidence, symptoms, severity, precautions, medicines):
    symptom_text = ", ".join(s.replace("_", " ") for s in symptoms)
    precaution_text = "; ".join(precautions)
    medicine_text = "; ".join(medicines)
    return (
        f"Based on the symptoms you reported ({symptom_text}), the assistant's "
        f"model predicts a {confidence:.1f}% likelihood that this matches "
        f"'{disease}', which is generally classified as {severity} in severity. "
        f"Recommended precautions include: {precaution_text}. "
        f"Commonly associated medicine categories: {medicine_text}. "
        f"This is an AI-generated preliminary suggestion, not a medical diagnosis or "
        f"prescription — please consult a licensed doctor before taking any medicine."
    )


def generate_explanation(disease: str, confidence: float, symptoms: list,
                          severity: str, precautions: list, medicines: list) -> str:
    """
    Returns a natural-language explanation of the diagnosis result.
    Uses OpenAI's GPT model when an API key is available, otherwise
    falls back to a deterministic template so the app never breaks.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key and _OPENAI_SDK_AVAILABLE:
        try:
            client = OpenAI(api_key=api_key)
            symptom_text = ", ".join(s.replace("_", " ") for s in symptoms)
            precaution_text = "; ".join(precautions)
            medicine_text = "; ".join(medicines)
            prompt = (
                f"A user reported these symptoms: {symptom_text}. "
                f"A machine learning model predicts the condition '{disease}' "
                f"with {confidence:.1f}% confidence, severity level '{severity}'. "
                f"Suggested precautions: {precaution_text}. "
                f"Commonly associated OTC/medicine categories (NOT a prescription): {medicine_text}. "
                f"Write a short (5-7 sentence), warm, clear explanation for the "
                f"user summarizing this prediction, precautions, and medicine "
                f"categories in simple language. Clearly state that any "
                f"prescription-only medicine must be taken only after a doctor's "
                f"confirmation, and end with a reminder that this is not a "
                f"substitute for professional medical advice."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful, careful health information assistant. You never give a final diagnosis, only preliminary, educational guidance."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.6,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # network issues, invalid key, quota, etc.
            fallback = _template_fallback(disease, confidence, symptoms, severity, precautions, medicines)
            return fallback + f"\n\n[Note: Generative AI call failed, showing rule-based summary. Reason: {exc}]"

    return _template_fallback(disease, confidence, symptoms, severity, precautions, medicines)
