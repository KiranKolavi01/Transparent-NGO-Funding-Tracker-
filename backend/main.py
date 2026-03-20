from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="NGO Transparency API", description="Backend API for Transparent NGO Funding Tracker")

# --- 1. ADD CORS SUPPORT ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. ENSURE GLOBAL IN-MEMORY STORAGE ---
donors_db = []

donations_db = [
    {"donor_name": "Alice Smith", "project": "Clean Water Initiative", "amount": 500, "date": "2026-03-01"},
    {"donor_name": "Bob Jones", "project": "Education for All", "amount": 1500, "date": "2026-03-05"},
    {"donor_name": "Charlie Brown", "project": "Health Clinics Setup", "amount": 300, "date": "2026-03-10"},
    {"donor_name": "Diana Prince", "project": "Clean Water Initiative", "amount": 750, "date": "2026-03-12"},
    {"donor_name": "Evan Wright", "project": "Reforestation Project", "amount": 200, "date": "2026-03-15"},
]

project_stats_db = {
    "budget_allocation": {
        "Infrastructure": 4500,
        "Supplies": 2300,
        "Logistics": 1200,
        "Operations": 1000,
        "Marketing": 500
    },
    "total_spent": 5800,
    "target_goal": 15000
}


# --- 3. ADD Pydantic VALIDATION MODELS ---
class DonorCreate(BaseModel):
    name: str
    email: str

class DonationCreate(BaseModel):
    donor_name: str
    project: str
    amount: float


# --- 6. ADD ROOT ENDPOINT ---
@app.get("/")
def read_root():
    return {"message": "API Running"}


# --- 7. ADD HEALTH CHECK ENDPOINT ---
@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- EXISTING API ROUTES ---

@app.post("/api/register")
def register_donor(donor: DonorCreate):
    # ADDED: Input Sanitization (Light)
    clean_name = donor.name.strip()
    clean_email = donor.email.strip()

    if not clean_name or not clean_email:
        raise HTTPException(status_code=400, detail="Name and email are required")
        
    # FIXED: Case-insensitive duplicate donor registration check
    if any(d["email"].lower() == clean_email.lower() for d in donors_db):
        raise HTTPException(status_code=400, detail="Donor already exists")
        
    new_donor = {
        "name": clean_name,
        "email": clean_email
    }
    donors_db.append(new_donor)
    
    # --- 5. STANDARDIZE RESPONSE FORMAT ---
    return {
        "success": True,
        "message": "Donor registered successfully",
        "data": new_donor
    }

@app.post("/api/donate")
def make_donation(donation: DonationCreate):
    # ADDED: Input Sanitization (Light)
    clean_donor_name = donation.donor_name.strip()
    clean_project = donation.project.strip()

    if not clean_donor_name or not clean_project:
        raise HTTPException(status_code=400, detail="Invalid donation data")
        
    # FIXED: Safe amount validation
    if donation.amount is None or donation.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid donation amount")
        
    # FIXED: Relaxed donor existing validation & Case-insensitive matching
    if donors_db and not any(d["name"].strip().lower() == clean_donor_name.lower() for d in donors_db):
        raise HTTPException(status_code=400, detail="Donor not registered")

    new_donation = {
        "donor_name": clean_donor_name,
        "project": clean_project, 
        "amount": donation.amount,
        # --- 4. ADD AUTOMATIC DATE HANDLING ---
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    # FIXED: Ensure donations ALWAYS append safely
    donations_db.append(new_donation)
    
    # --- 5. STANDARDIZE RESPONSE FORMAT ---
    return {
        "success": True,
        "message": "Donation successful",
        "data": new_donation
    }

@app.get("/api/donations")
def get_all_donations():
    return {
        "success": True,
        "message": "Donations retrieved successfully",
        "data": donations_db,
        "donations": donations_db  # Preserved to ensure frontend backwards compatibility
    }

@app.get("/api/dashboard-stats")
def get_dashboard_stats():
    return {
        "success": True,
        "message": "Stats retrieved successfully",
        "data": project_stats_db,
        "project_stats": project_stats_db  # Preserved to ensure frontend backwards compatibility
    }

@app.get("/api/donors")
def get_all_donors():
    return {
        "success": True,
        "message": "Donors retrieved successfully",
        "data": donors_db,
        "donors": donors_db  # Preserved to ensure frontend backwards compatibility
    }
