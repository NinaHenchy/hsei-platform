"""
HSEI Platform Configuration
=============================
HSE Incident Analytics & Process Safety Intelligence Platform
Facility: Offshore Production Complex OPC-Alpha
Regulatory Standards: API RP 754, OSHA 29 CFR 1910.119, ISO 45001, RIDDOR
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# BASE PATHS
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
SQLITE_DB_PATH = BASE_DIR / "database" / "hsei_dev.db"
POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hsei_user:hsei_pass@localhost:5432/hsei_db"
)

# ─────────────────────────────────────────────
# FACILITY CONFIGURATION
# ─────────────────────────────────────────────
FACILITY_NAME = "Offshore Production Complex — OPC-Alpha"
FACILITY_CODE = "OPC-A"
OPERATING_COMPANY = "ORPMI Energy Operations"
FIELD_NAME = "Alpha Field Development"
WORKFORCE_SIZE = 285
WORKING_HOURS_PER_SHIFT = 12
SHIFTS_PER_DAY = 2
CONTRACT_WORKERS_PCT = 0.35

# ─────────────────────────────────────────────
# API RP 754 PROCESS SAFETY EVENT TIERS
# ─────────────────────────────────────────────
# API RP 754 defines four tiers of process safety events
# Tier 1 = most severe (loss of containment with consequences)
# Tier 4 = leading indicators (near misses, demands on safety systems)

API_RP_754_TIERS = {
    "Tier 1": {
        "description": "LOPC with defined consequences — fire, explosion, injury, evacuation",
        "severity_weight": 10,
        "regulatory_reportable": True,
        "color": "#c0392b",
    },
    "Tier 2": {
        "description": "LOPC exceeding threshold without Tier 1 consequences",
        "severity_weight": 7,
        "regulatory_reportable": True,
        "color": "#e67e22",
    },
    "Tier 3": {
        "description": "Loss of primary containment — challenges to safety systems",
        "severity_weight": 4,
        "regulatory_reportable": False,
        "color": "#f39c12",
    },
    "Tier 4": {
        "description": "Near misses, demands on safety systems, unsafe acts/conditions",
        "severity_weight": 1,
        "regulatory_reportable": False,
        "color": "#27ae60",
    },
}

# ─────────────────────────────────────────────
# INCIDENT TYPES — ISO 45001 / OSHA ALIGNED
# ─────────────────────────────────────────────
INCIDENT_TYPES = [
    "Fatality",
    "Lost Time Injury",
    "Restricted Work Case",
    "Medical Treatment Case",
    "First Aid Case",
    "Near Miss",
    "Dangerous Occurrence",
    "Process Safety Event",
    "Environmental Release",
    "Property Damage",
    "Unsafe Act",
    "Unsafe Condition",
    "Vehicle Incident",
    "Fire / Explosion",
    "Spill / Release",
]

# ─────────────────────────────────────────────
# INCIDENT CATEGORIES — API RP 754 / OSHA ALIGNED
# ─────────────────────────────────────────────
INCIDENT_CATEGORIES = [
    "Mechanical / Equipment Failure",
    "Process Deviation",
    "Human Factors / Operator Error",
    "Slips, Trips and Falls",
    "Struck By / Against",
    "Caught In / Between",
    "Electrical Hazard",
    "Chemical Exposure",
    "Fire and Explosion",
    "Lifting and Rigging",
    "Working at Height",
    "Confined Space",
    "Hot Work",
    "Dropped Object",
    "Ergonomic / Manual Handling",
    "Environmental Release",
    "Vehicle / Transportation",
    "Contractor Management",
]

# ─────────────────────────────────────────────
# WORK AREAS / LOCATIONS
# ─────────────────────────────────────────────
WORK_AREAS = [
    "Production Deck",
    "Wellhead Area",
    "Gas Compression Module",
    "Chemical Injection Skid",
    "Utilities Module",
    "Accommodation Block",
    "Helideck",
    "Crane / Lifting Zone",
    "Storage Tank Farm",
    "Electrical Room",
    "Control Room",
    "Workshop",
    "Piping Corridor",
    "Flare Boom",
    "Marine / Boat Landing",
]

# ─────────────────────────────────────────────
# DEPARTMENTS
# ─────────────────────────────────────────────
DEPARTMENTS = [
    "Production Operations",
    "Maintenance",
    "Drilling",
    "Logistics",
    "HSE",
    "Instrumentation & Control",
    "Electrical",
    "Process Engineering",
    "Contractor — Mechanical",
    "Contractor — Civil",
    "Contractor — Catering",
]

# ─────────────────────────────────────────────
# BODY PARTS — OSHA RECORDKEEPING
# ─────────────────────────────────────────────
BODY_PARTS = [
    "Head / Skull", "Eye", "Face", "Neck",
    "Shoulder", "Arm", "Hand / Fingers", "Wrist",
    "Back / Spine", "Chest / Torso", "Hip",
    "Leg / Knee", "Foot / Ankle", "Multiple",
    "No Injury",
]

# ─────────────────────────────────────────────
# ROOT CAUSE CATEGORIES — BOW-TIE / ICAM ALIGNED
# ─────────────────────────────────────────────
ROOT_CAUSE_CATEGORIES = [
    "Inadequate Procedure / No Procedure",
    "Procedure Not Followed",
    "Inadequate Training / Competency",
    "Inadequate Supervision",
    "Equipment Design Deficiency",
    "Equipment Failure / Deterioration",
    "Inadequate Hazard Identification",
    "Management System Deficiency",
    "Communication Failure",
    "Time Pressure / Workload",
    "Fatigue",
    "Environmental Conditions",
    "Contractor Management Gap",
    "Change Management Failure",
]

# ─────────────────────────────────────────────
# KPI THRESHOLDS — INDUSTRY BENCHMARKS
# ─────────────────────────────────────────────
KPI_THRESHOLDS = {
    # TRIR: Total Recordable Incident Rate (per 200,000 man-hours)
    # O&G industry average: ~0.8 | World class: <0.3
    "trir_green": 0.30,
    "trir_amber": 0.80,
    "trir_red": 1.50,

    # LTIR: Lost Time Incident Rate (per 200,000 man-hours)
    # O&G industry average: ~0.25 | World class: <0.10
    "ltir_green": 0.10,
    "ltir_amber": 0.25,
    "ltir_red": 0.50,

    # Near Miss Reporting Rate — higher is BETTER (reporting culture)
    "nmrr_green": 5.0,   # >5 near misses reported per recordable = good culture
    "nmrr_amber": 2.0,
    "nmrr_red": 1.0,

    # Safety Observation Completion Rate
    "obs_completion_green": 90,
    "obs_completion_amber": 75,
    "obs_completion_red": 60,

    # Action Close-Out Rate
    "action_closeout_green": 85,
    "action_closeout_amber": 70,
    "action_closeout_red": 55,

    # HSE Training Compliance
    "training_green": 95,
    "training_amber": 85,
    "training_red": 75,
}

# ─────────────────────────────────────────────
# SIMULATION PARAMETERS
# ─────────────────────────────────────────────
SIMULATION_DAYS = 365
SIMULATION_START = "2024-01-01"
SIMULATION_END = "2024-12-31"
RANDOM_SEED = 42

# ─────────────────────────────────────────────
# REGULATORY BODIES
# ─────────────────────────────────────────────
REGULATORY_BODIES = {
    "NUPRC": "Nigerian Upstream Petroleum Regulatory Commission",
    "NOSDRA": "National Oil Spill Detection and Response Agency",
    "OSHA": "Occupational Safety and Health Administration",
    "IADC": "International Association of Drilling Contractors",
    "IMO": "International Maritime Organization",
}

# ─────────────────────────────────────────────
# COST PARAMETERS
# ─────────────────────────────────────────────
INCIDENT_COST_ESTIMATES = {
    "Fatality":               4500000,
    "Lost Time Injury":        85000,
    "Restricted Work Case":    25000,
    "Medical Treatment Case":   8500,
    "First Aid Case":           1200,
    "Near Miss":                  500,
    "Dangerous Occurrence":    45000,
    "Process Safety Event":   320000,
    "Environmental Release":  180000,
    "Property Damage":         35000,
    "Unsafe Act":                 200,
    "Unsafe Condition":           300,
    "Vehicle Incident":         15000,
    "Fire / Explosion":        750000,
    "Spill / Release":         120000,
}
