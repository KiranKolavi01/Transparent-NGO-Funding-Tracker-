from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI(title="NGO Transparency API", description="Backend API for Transparent NGO Funding Tracker")

# --- CORS SUPPORT ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SQLITE SETUP ---
def get_db_connection():
    conn = sqlite3.connect("ngo.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    try:
        # Donors table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS donors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        """)
        # Donations table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_name TEXT NOT NULL,
                project TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)
        # Expenses table (REQUIRED for problem statement)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                purpose TEXT NOT NULL,
                amount REAL NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()

# Initialize database on startup
init_db()

# --- Pydantic MODELS ---
class DonorCreate(BaseModel):
    name: str
    email: str

class DonationCreate(BaseModel):
    donor_name: str
    project: str
    amount: float

# --- API ROUTES ---

@app.get("/")
def read_root():
    return {"message": "NGO Transparency API Running"}

@app.post("/api/register")
def register_donor(donor: DonorCreate):
    name = (donor.name or "").strip()
    email = (donor.email or "").strip().lower()
    
    if not name or not email:
        raise HTTPException(status_code=400, detail="Name and email are required")
        
    conn = get_db_connection()
    try:
        # Check for duplicate email (case-insensitive)
        existing = conn.execute("SELECT 1 FROM donors WHERE LOWER(email) = ?", (email,)).fetchone()
        if existing:
            return {"success": False, "message": "Email already registered", "data": None}
            
        conn.execute("INSERT INTO donors (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
    finally:
        conn.close()
        
    return {"success": True, "message": "Donor registered successfully", "data": {"name": name, "email": email}}

@app.post("/api/donate")
def make_donation(donation: DonationCreate):
    donor_name = (donation.donor_name or "").strip()
    project = (donation.project or "").strip()
    
    if donation.amount <= 0:
        return {"success": False, "message": "Amount must be greater than 0", "data": None}
    
    conn = get_db_connection()
    try:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO donations (donor_name, project, amount, date) VALUES (?, ?, ?, ?)",
            (donor_name, project, donation.amount, date)
        )
        conn.commit()
        result = {"donor_name": donor_name, "project": project, "amount": donation.amount, "date": date}
    finally:
        conn.close()
        
    return {"success": True, "message": "Donation recorded", "data": result, "donations": result}

@app.get("/api/donations")
def get_all_donations():
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT donor_name, project, amount, date FROM donations ORDER BY id DESC").fetchall()
        donations = [dict(row) for row in rows]
    finally:
        conn.close()
    return {"success": True, "message": "Success", "data": donations, "donations": donations}

@app.get("/api/donors")
def get_all_donors():
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT name, email FROM donors ORDER BY id ASC").fetchall()
        donors = [dict(row) for row in rows]
    finally:
        conn.close()
    return {"success": True, "message": "Success", "data": donors, "donors": donors}

@app.get("/api/dashboard-stats")
def get_dashboard_stats():
    # Placeholder for project stats logic if needed; returning standard structure
    # For compatibility, using fixed stats or dynamic based on donations/expenses
    conn = get_db_connection()
    try:
        total_donated = conn.execute("SELECT SUM(amount) FROM donations").fetchone()[0] or 0
        total_spent = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0
    finally:
        conn.close()
        
    stats = {
        "budget_allocation": {
            "Infrastructure": 4500,
            "Supplies": 2300,
            "Logistics": 1200,
            "Operations": 1000,
            "Marketing": 500,
        },
        "total_donated": total_donated,
        "total_spent": total_spent,
        "target_goal": 15000,
    }
    return {
        "success": True,
        "message": "Stats retrieved successfully",
        "data": stats,
        "project_stats": stats
    }
