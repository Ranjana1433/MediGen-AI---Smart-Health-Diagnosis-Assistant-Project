"""
Static reference data used to enrich ML predictions with
precautions, common medicine categories, and a severity label.

IMPORTANT: The "medicines" listed here are general, commonly known
OTC (over-the-counter) medicine categories for educational/academic
project purposes only. They are NOT a prescription. Dosage always
depends on age, weight, allergies, and other conditions, so a
qualified doctor/pharmacist must always be consulted before taking
any medicine. In a real deployment this would come from a verified
medical knowledge base, not hardcoded data.
"""

MEDICAL_DISCLAIMER = (
    "These are general OTC medicine categories for educational purposes only, "
    "not a prescription. Dosage and suitability depend on age, weight, allergies, "
    "pregnancy status, and other conditions. Always consult a licensed doctor or "
    "pharmacist before taking any medicine."
)

DISEASE_INFO = {
    "Common Cold": {
        "severity": "Mild",
        "specialist": "General Physician",
        "precautions": [
            "Stay hydrated and rest well",
            "Use steam inhalation for congestion",
            "Take warm fluids like soup or herbal tea",
            "Consult a doctor if symptoms persist beyond 7 days",
        ],
        "medicines": [
            "Paracetamol - for mild fever/body ache",
            "Cetirizine or other antihistamine - for runny nose/sneezing",
            "Saline nasal drops/spray - for congestion",
            "Throat lozenges - for sore throat relief",
        ],
    },
    "Influenza (Flu)": {
        "severity": "Moderate",
        "specialist": "General Physician",
        "precautions": [
            "Rest and stay hydrated",
            "Take fever-reducing medication if advised by a doctor",
            "Avoid contact with others to prevent spread",
            "Seek medical attention if breathing difficulty occurs",
        ],
        "medicines": [
            "Paracetamol - for fever and body ache",
            "Oseltamivir (Tamiflu) - antiviral, PRESCRIPTION ONLY, doctor-directed",
            "Cough syrup (as advised by pharmacist) - for persistent cough",
            "ORS - to prevent dehydration",
        ],
    },
    "COVID-19": {
        "severity": "Moderate to Severe",
        "specialist": "Pulmonologist",
        "precautions": [
            "Isolate yourself from others immediately",
            "Monitor oxygen levels regularly",
            "Get tested (RT-PCR/RAT) to confirm",
            "Seek emergency care if breathlessness or chest pain occurs",
        ],
        "medicines": [
            "Paracetamol - for fever/body ache",
            "Multivitamins (Vitamin C, D, Zinc) - general immune support",
            "Antiviral/steroid medication - PRESCRIPTION ONLY, doctor-directed based on severity",
            "Pulse oximeter monitoring recommended alongside any medication",
        ],
    },
    "Migraine": {
        "severity": "Mild to Moderate",
        "specialist": "Neurologist",
        "precautions": [
            "Rest in a dark, quiet room",
            "Stay hydrated and avoid known triggers",
            "Consider over-the-counter pain relief if appropriate",
            "Consult a neurologist for frequent episodes",
        ],
        "medicines": [
            "Paracetamol or Ibuprofen - for mild-moderate pain relief",
            "Triptans (e.g., Sumatriptan) - PRESCRIPTION ONLY, for moderate-severe migraine",
            "Anti-nausea medication - if migraine is accompanied by nausea",
        ],
    },
    "Food Poisoning": {
        "severity": "Moderate",
        "specialist": "Gastroenterologist",
        "precautions": [
            "Stay hydrated with oral rehydration solution",
            "Avoid solid food until vomiting subsides",
            "Rest and avoid dairy/spicy food temporarily",
            "Seek medical care if symptoms last more than 2 days",
        ],
        "medicines": [
            "ORS (Oral Rehydration Solution) - to prevent dehydration",
            "Probiotics - to restore gut bacteria",
            "Antiemetics (for vomiting) - PRESCRIPTION/pharmacist-guided",
            "Antibiotics - ONLY if a doctor confirms bacterial infection",
        ],
    },
    "Malaria": {
        "severity": "Severe",
        "specialist": "Infectious Disease Specialist",
        "precautions": [
            "Seek immediate medical testing and treatment",
            "Use mosquito nets and repellents to prevent spread",
            "Stay hydrated and rest",
            "Do not self-medicate with antimalarials",
        ],
        "medicines": [
            "Antimalarial drugs (e.g., Chloroquine, Artemisinin-based combination) - PRESCRIPTION ONLY after confirmed blood test",
            "Paracetamol - for fever, NOT Aspirin/Ibuprofen without doctor advice",
            "IV fluids - if prescribed for severe dehydration",
        ],
    },
    "Typhoid": {
        "severity": "Severe",
        "specialist": "General Physician",
        "precautions": [
            "Consult a doctor for antibiotic treatment",
            "Drink only boiled or purified water",
            "Maintain a light, easily digestible diet",
            "Complete the full prescribed antibiotic course",
        ],
        "medicines": [
            "Antibiotics (e.g., Ciprofloxacin, Azithromycin) - PRESCRIPTION ONLY, complete full course",
            "Paracetamol - for fever",
            "ORS - to maintain hydration",
        ],
    },
    "Dengue": {
        "severity": "Severe",
        "specialist": "Infectious Disease Specialist",
        "precautions": [
            "Seek immediate medical attention and platelet monitoring",
            "Stay hydrated with fluids and ORS",
            "Avoid aspirin/NSAIDs (can worsen bleeding risk)",
            "Use mosquito protection to avoid further spread",
        ],
        "medicines": [
            "Paracetamol ONLY - for fever (Aspirin/Ibuprofen strictly avoided, bleeding risk)",
            "ORS and fluids - to maintain platelet/fluid balance",
            "Hospitalization/IV therapy - PRESCRIPTION ONLY if platelet count drops significantly",
        ],
    },
    "Hypertension": {
        "severity": "Moderate to Severe",
        "specialist": "Cardiologist",
        "precautions": [
            "Monitor blood pressure regularly",
            "Reduce salt intake and manage stress",
            "Consult a physician for medication management",
            "Seek emergency care for severe headache with chest pain",
        ],
        "medicines": [
            "ACE inhibitors (e.g., Enalapril) - PRESCRIPTION ONLY",
            "Beta-blockers (e.g., Atenolol) - PRESCRIPTION ONLY",
            "Diuretics - PRESCRIPTION ONLY, dosage varies per patient",
            "Never self-adjust BP medication dosage without a doctor",
        ],
    },
    "Gastritis": {
        "severity": "Mild to Moderate",
        "specialist": "Gastroenterologist",
        "precautions": [
            "Avoid spicy, oily, and acidic foods",
            "Eat smaller, frequent meals",
            "Avoid NSAIDs and alcohol",
            "Consult a doctor if pain persists or worsens",
        ],
        "medicines": [
            "Antacids (e.g., Magnesium/Aluminum hydroxide) - for quick relief",
            "Proton Pump Inhibitors (e.g., Omeprazole) - reduces acid production",
            "H2 blockers (e.g., Ranitidine/Famotidine) - as advised by pharmacist",
        ],
    },
}


def get_disease_info(disease: str) -> dict:
    return DISEASE_INFO.get(
        disease,
        {
            "severity": "Unknown",
            "specialist": "General Physician",
            "precautions": ["Please consult a certified medical professional."],
            "medicines": ["No medicine data available. Please consult a doctor."],
        },
    )
