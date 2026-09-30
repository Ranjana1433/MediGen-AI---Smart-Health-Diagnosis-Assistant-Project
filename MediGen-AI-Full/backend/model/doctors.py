"""
Static doctor roster used for the appointment booking feature.
In a real deployment this would come from a hospital/clinic database;
for this academic project it is hardcoded reference data.
"""

DOCTORS = [
    {
        "id": "doc1",
        "name": "Dr. Aakriti Sharma",
        "specialty": "General Physician",
        "available_days": "Mon–Sat",
        "available_slots": ["09:00 AM", "11:00 AM", "02:00 PM", "05:00 PM"],
    },
    {
        "id": "doc2",
        "name": "Dr. Rohan Mehta",
        "specialty": "Cardiologist",
        "available_days": "Mon, Wed, Fri",
        "available_slots": ["10:00 AM", "12:00 PM", "04:00 PM"],
    },
    {
        "id": "doc3",
        "name": "Dr. Neha Kapoor",
        "specialty": "Neurologist",
        "available_days": "Tue, Thu, Sat",
        "available_slots": ["09:30 AM", "01:00 PM", "03:30 PM"],
    },
    {
        "id": "doc4",
        "name": "Dr. Sameer Iyer",
        "specialty": "Gastroenterologist",
        "available_days": "Mon–Fri",
        "available_slots": ["10:30 AM", "02:30 PM", "06:00 PM"],
    },
    {
        "id": "doc5",
        "name": "Dr. Priya Nair",
        "specialty": "Pulmonologist",
        "available_days": "Wed–Sat",
        "available_slots": ["09:00 AM", "11:30 AM", "04:30 PM"],
    },
    {
        "id": "doc6",
        "name": "Dr. Arjun Verma",
        "specialty": "Infectious Disease Specialist",
        "available_days": "Mon, Tue, Thu",
        "available_slots": ["10:00 AM", "01:30 PM", "05:00 PM"],
    },
]


def get_doctors_by_specialty(specialty: str = None):
    if not specialty:
        return DOCTORS
    return [d for d in DOCTORS if d["specialty"] == specialty] or DOCTORS


def get_doctor_by_id(doctor_id: str):
    for d in DOCTORS:
        if d["id"] == doctor_id:
            return d
    return None
