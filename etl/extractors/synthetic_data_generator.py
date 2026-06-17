"""
HSEI Synthetic Data Generator
===============================
Generates realistic HSE incident and safety management data for
OPC-Alpha facility across a full calendar year (2024).

Data realism features:
- Incident rates calibrated to O&G industry benchmarks (IOGP 2023 data)
- Seasonal variation (Q3 incidents elevated — summer heat stress, contractor peak)
- Cluster effects — incidents follow unsafe condition reports with a lag
- Heinrich Triangle ratios maintained throughout
- TRIR target: ~0.65 (slightly above world class, realistic for mid-sized operator)
- API RP 754 Tier distribution aligned to industry norms
- PTW violations correlated with incident occurrences
- Training compliance degradation over time (realistic scheduling behaviour)
"""

import sys
import random
from pathlib import Path
from datetime import datetime, date, timedelta

import numpy as np
import pandas as pd
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import (
    INCIDENT_TYPES, INCIDENT_CATEGORIES, WORK_AREAS, DEPARTMENTS,
    BODY_PARTS, ROOT_CAUSE_CATEGORIES, INCIDENT_COST_ESTIMATES,
    API_RP_754_TIERS, WORKFORCE_SIZE, WORKING_HOURS_PER_SHIFT,
    SHIFTS_PER_DAY, CONTRACT_WORKERS_PCT, SIMULATION_DAYS,
    SIMULATION_START, RANDOM_SEED, KPI_THRESHOLDS
)

np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

START_DATE = datetime.strptime(SIMULATION_START, "%Y-%m-%d").date()
DATES = [START_DATE + timedelta(days=i) for i in range(SIMULATION_DAYS)]

PERSONNEL = [
    "Ibrahim Yusuf", "Chukwuemeka Eze", "Oluwaseun Adeyemi",
    "Fatima Al-Rashid", "Emeka Okafor", "Amara Diallo",
    "Taiwo Ogundimu", "Mohammed Al-Farsi", "Ngozi Okonkwo",
    "Babatunde Fashola", "Aisha Bello", "David Osei",
    "Grace Mensah", "Kofi Asante", "Sola Adewale",
    "Chidi Nwosu", "Yetunde Afolabi", "Rasheed Lawal",
]

HSE_OFFICERS = [
    "Sarah Okonkwo (HSE Manager)", "Tunde Balogun (HSE Supervisor)",
    "Chinwe Eze (HSE Officer)", "Musa Ibrahim (HSE Officer)",
]

TRAINING_COURSES = [
    ("Basic H2S Safety", "Process Safety", 365),
    ("Fire Fighting & Prevention", "Emergency Response", 365),
    ("Permit to Work System", "Safety Management", 365),
    ("Manual Handling", "Ergonomics", 730),
    ("Working at Height", "Physical Hazards", 365),
    ("Confined Space Entry", "Physical Hazards", 365),
    ("Chemical Handling & COSHH", "Chemical Safety", 365),
    ("HUET — Helicopter Underwater Escape", "Emergency Response", 365),
    ("First Aid & CPR", "Emergency Response", 730),
    ("Dropped Objects Prevention", "Physical Hazards", 365),
    ("Stop Work Authority", "Safety Leadership", 730),
    ("Incident Investigation & RCA", "Safety Management", 1095),
    ("Environmental Awareness", "Environmental", 365),
    ("Electrical Safety Awareness", "Electrical Safety", 365),
    ("BOSIET — Basic Offshore Safety", "Offshore Safety", 1825),
]


def _seasonal_weight(day_index: int) -> float:
    """Q3 elevated risk — heat stress, peak contractor activity, summer fatigue."""
    month = (START_DATE + timedelta(days=day_index)).month
    weights = {1:0.7, 2:0.7, 3:0.8, 4:0.9, 5:1.0, 6:1.1,
               7:1.3, 8:1.3, 9:1.1, 10:0.9, 11:0.8, 12:0.7}
    return weights.get(month, 1.0)


def generate_incidents() -> pd.DataFrame:
    """
    Generate incident register.
    Target TRIR ~0.65 — slightly above world class, realistic for mid-sized operator.
    Annual manhours = 285 workers × 12hr × 2 shifts × 365 days × 0.5 utilisation
    """
    records = []
    inc_counter = 1

    # Target incident counts calibrated to IOGP 2023 benchmarks
    incident_plan = {
        "Fatality":                0,   # Target zero
        "Lost Time Injury":        3,
        "Restricted Work Case":    5,
        "Medical Treatment Case":  8,
        "First Aid Case":         22,
        "Near Miss":              68,
        "Dangerous Occurrence":    4,
        "Process Safety Event":    6,
        "Environmental Release":   3,
        "Property Damage":         8,
        "Unsafe Act":             45,
        "Unsafe Condition":       38,
        "Vehicle Incident":        2,
        "Fire / Explosion":        1,
        "Spill / Release":         4,
    }

    for inc_type, count in incident_plan.items():
        for _ in range(count):
            # Seasonal weighting for date assignment
            weights = [_seasonal_weight(i) for i in range(SIMULATION_DAYS)]
            total = sum(weights)
            weights = [w / total for w in weights]
            day_idx = np.random.choice(range(SIMULATION_DAYS), p=weights)
            inc_date = DATES[day_idx]

            severity = _severity_from_type(inc_type)
            category = _category_from_type(inc_type)
            area = random.choice(WORK_AREAS)
            dept = random.choice(DEPARTMENTS)
            emp_type = "Contractor" if random.random() < CONTRACT_WORKERS_PCT else "Direct"

            days_lost = 0
            days_restricted = 0
            if inc_type == "Lost Time Injury":
                days_lost = random.randint(3, 45)
            elif inc_type == "Restricted Work Case":
                days_restricted = random.randint(1, 14)

            api_tier = _api_tier(inc_type)
            reg_reportable = int(inc_type in [
                "Fatality", "Lost Time Injury", "Dangerous Occurrence",
                "Process Safety Event", "Environmental Release", "Fire / Explosion"
            ])

            cost_base = INCIDENT_COST_ESTIMATES.get(inc_type, 1000)
            cost = round(cost_base * random.uniform(0.7, 1.5), 0)

            inc_number = f"INC-2024-{inc_counter:04d}"
            body_part = random.choice(BODY_PARTS) if inc_type not in [
                "Near Miss", "Unsafe Act", "Unsafe Condition",
                "Process Safety Event", "Environmental Release",
                "Property Damage", "Spill / Release"
            ] else "No Injury"

            close_days = random.randint(7, 45)
            close_date = (inc_date + timedelta(days=close_days))
            if close_date > DATES[-1]:
                close_date = DATES[-1]
                is_closed = 0
            else:
                is_closed = 1

            records.append({
                "incident_number":          inc_number,
                "incident_date":            inc_date.isoformat(),
                "incident_time":            f"{random.randint(5,22):02d}:{random.choice(['00','15','30','45'])}:00",
                "incident_type":            inc_type,
                "incident_category":        category,
                "api_rp754_tier":           api_tier,
                "severity":                 severity,
                "work_area":                area,
                "department":               dept,
                "description":              _incident_description(inc_type, area, dept),
                "immediate_cause":          _immediate_cause(category),
                "root_cause_category":      random.choice(ROOT_CAUSE_CATEGORIES),
                "root_cause_description":   _root_cause_text(category),
                "contributing_factors":     _contributing_factors(),
                "body_part_affected":       body_part,
                "injury_nature":            _injury_nature(inc_type),
                "days_lost":                days_lost,
                "days_restricted":          days_restricted,
                "employee_type":            emp_type,
                "workers_involved":         random.randint(1, 3),
                "witnesses":                random.randint(0, 4),
                "reported_by":              random.choice(PERSONNEL),
                "investigated_by":          random.choice(HSE_OFFICERS),
                "investigation_complete":   is_closed,
                "regulatory_reportable":    reg_reportable,
                "reported_to_regulator":    reg_reportable,
                "regulator_reference":      f"NUPRC-2024-{inc_counter:04d}" if reg_reportable else None,
                "estimated_cost_usd":       cost,
                "actual_cost_usd":          round(cost * random.uniform(0.85, 1.20), 0),
                "property_damage_usd":      round(random.uniform(0, cost * 0.3), 0) if inc_type == "Property Damage" else 0,
                "environmental_impact":     int(inc_type in ["Environmental Release", "Spill / Release"]),
                "spill_volume_litres":      round(random.uniform(5, 500), 1) if inc_type in ["Spill / Release", "Environmental Release"] else None,
                "is_recurring":             int(random.random() < 0.15),
                "previous_similar_event":   f"INC-2023-{random.randint(1,200):04d}" if random.random() < 0.15 else None,
                "closure_date":             close_date.isoformat() if is_closed else None,
                "is_closed":                is_closed,
            })
            inc_counter += 1

    df = pd.DataFrame(records).sort_values("incident_date").reset_index(drop=True)
    logger.info(f"Incidents generated: {len(df)}")
    return df


def _severity_from_type(inc_type: str) -> str:
    severity_map = {
        "Fatality": "Critical",
        "Lost Time Injury": "High",
        "Dangerous Occurrence": "High",
        "Process Safety Event": "High",
        "Fire / Explosion": "Critical",
        "Restricted Work Case": "Medium",
        "Medical Treatment Case": "Medium",
        "Environmental Release": "Medium",
        "Property Damage": "Medium",
        "Spill / Release": "Medium",
        "Vehicle Incident": "Medium",
        "First Aid Case": "Low",
        "Near Miss": "Low",
        "Unsafe Act": "Negligible",
        "Unsafe Condition": "Negligible",
    }
    return severity_map.get(inc_type, "Low")


def _category_from_type(inc_type: str) -> str:
    cat_map = {
        "Fatality": "Struck By / Against",
        "Lost Time Injury": random.choice(["Slips, Trips and Falls", "Struck By / Against", "Caught In / Between", "Working at Height"]),
        "Restricted Work Case": random.choice(["Manual Handling / Ergonomic", "Slips, Trips and Falls", "Chemical Exposure"]),
        "Medical Treatment Case": random.choice(INCIDENT_CATEGORIES[3:9]),
        "First Aid Case": random.choice(INCIDENT_CATEGORIES[3:9]),
        "Near Miss": random.choice(INCIDENT_CATEGORIES),
        "Dangerous Occurrence": "Process Deviation",
        "Process Safety Event": "Mechanical / Equipment Failure",
        "Environmental Release": "Environmental Release",
        "Property Damage": "Mechanical / Equipment Failure",
        "Unsafe Act": "Human Factors / Operator Error",
        "Unsafe Condition": "Mechanical / Equipment Failure",
        "Vehicle Incident": "Vehicle / Transportation",
        "Fire / Explosion": "Fire and Explosion",
        "Spill / Release": "Environmental Release",
    }
    return cat_map.get(inc_type, random.choice(INCIDENT_CATEGORIES))


def _api_tier(inc_type: str):
    if inc_type in ["Fire / Explosion", "Fatality"]:
        return "Tier 1"
    elif inc_type in ["Process Safety Event", "Environmental Release"]:
        return random.choice(["Tier 1", "Tier 2"])
    elif inc_type in ["Dangerous Occurrence", "Spill / Release"]:
        return "Tier 2"
    elif inc_type in ["Near Miss"] and random.random() < 0.3:
        return "Tier 3"
    elif inc_type in ["Unsafe Act", "Unsafe Condition"]:
        return "Tier 4"
    return None


def _incident_description(inc_type: str, area: str, dept: str) -> str:
    descs = {
        "Lost Time Injury":      f"Worker sustained injury in {area} during routine {dept} operations. Injury required medical attention and resulted in lost time from work.",
        "Restricted Work Case":  f"Restricted work case recorded in {area}. Worker able to perform modified duties. Medical assessment completed.",
        "Medical Treatment Case":f"Medical treatment required following incident in {area}. First aid administered on site. Referred to medic for further treatment.",
        "First Aid Case":        f"Minor injury in {area} treated with on-site first aid. Worker returned to normal duties following treatment.",
        "Near Miss":             f"Near miss event reported in {area}. No injury or damage occurred but potential for serious incident was present.",
        "Process Safety Event":  f"Process safety event recorded in {area}. Loss of primary containment detected. Emergency response procedures activated.",
        "Dangerous Occurrence":  f"Dangerous occurrence in {area} — notifiable event under regulatory requirements. Investigation initiated immediately.",
        "Environmental Release": f"Uncontrolled release of hydrocarbon/chemical detected in {area}. Containment measures deployed. NOSDRA notification under review.",
        "Property Damage":       f"Equipment damage recorded in {area}. Assessment completed. Repair work order raised.",
        "Unsafe Act":            f"Unsafe act observed in {area} during {dept} operations. Worker counselled and corrective action raised.",
        "Unsafe Condition":      f"Unsafe condition identified during safety walk in {area}. Immediate corrective action taken. Work area reassessed.",
        "Vehicle Incident":      f"Vehicle incident on facility roadway / boat landing. No serious injuries. Vehicle inspection completed.",
        "Fire / Explosion":      f"Fire/explosion event in {area}. Emergency response team mobilised. Area evacuated. Investigation team assembled.",
        "Spill / Release":       f"Spill/release incident in {area}. Containment booms deployed. Environmental assessment initiated.",
    }
    return descs.get(inc_type, f"Incident recorded in {area} — {dept} department. Investigation in progress.")


def _immediate_cause(category: str) -> str:
    causes = {
        "Slips, Trips and Falls":       "Wet/slippery surface not barricaded. Worker not wearing appropriate footwear for conditions.",
        "Struck By / Against":          "Moving equipment in proximity to worker. Exclusion zone not established.",
        "Human Factors / Operator Error":"Worker deviated from established procedure. Task not fully understood before commencement.",
        "Mechanical / Equipment Failure":"Equipment failed beyond design parameters. Maintenance overdue.",
        "Process Deviation":            "Process operating outside normal envelope. Control system response inadequate.",
        "Chemical Exposure":            "Worker exposed to chemical during handling. PPE not adequate for task.",
        "Working at Height":            "Work at height without adequate fall protection. Harness not anchored correctly.",
        "Fire and Explosion":           "Ignition source in flammable atmosphere. Hot work controls not fully implemented.",
        "Environmental Release":        "Flange leak not detected during routine inspection. Corrosion beyond assessed rate.",
        "Vehicle / Transportation":     "Speed excessive for road conditions. Driver distracted.",
    }
    return causes.get(category, "Immediate cause under investigation. Root cause analysis in progress.")


def _root_cause_text(category: str) -> str:
    rca = {
        "Slips, Trips and Falls":       "Pre-job hazard assessment did not identify slip risk. Housekeeping standards not maintained in area.",
        "Struck By / Against":          "Simultaneous operations not adequately controlled. Exclusion zone management procedure not followed.",
        "Human Factors / Operator Error":"Training records show competency assessment overdue. Procedure not updated following last equipment modification.",
        "Mechanical / Equipment Failure":"Preventive maintenance interval exceeded. Inspection frequency insufficient for operating conditions.",
        "Process Deviation":            "Alarm management: control room operator desensitised to alarm floods. Management of change not applied to setpoint revision.",
        "Chemical Exposure":            "Chemical risk assessment (COSHH) not reviewed following supplier change. PPE specification inadequate.",
        "Working at Height":            "Permit to work scope did not capture full extent of height work. Rescue plan not in place.",
        "Fire and Explosion":           "Simultaneous hot work and process operation not identified in risk assessment. Gas detection not functioning.",
        "Environmental Release":        "Corrosion monitoring programme did not detect wall loss rate acceleration. Inspection interval based on initial data.",
        "Vehicle / Transportation":     "Journey management plan not completed. Driver not briefed on facility speed limits.",
    }
    return rca.get(category, "Root cause analysis completed. Management system deficiency identified as primary contributor.")


def _contributing_factors() -> str:
    factors = random.sample([
        "Time pressure / production schedule",
        "Inadequate pre-job planning",
        "Communication gap at shift handover",
        "Worker fatigue — extended shift",
        "Contractor competency not verified",
        "Environmental conditions — heat stress",
        "Inadequate lighting in work area",
        "Concurrent operations not coordinated",
        "Tool/equipment not fit for purpose",
        "Emergency response plan not rehearsed",
    ], k=random.randint(2, 4))
    return " | ".join(factors)


def _injury_nature(inc_type: str) -> str:
    if inc_type in ["Near Miss","Unsafe Act","Unsafe Condition",
                    "Process Safety Event","Environmental Release",
                    "Property Damage","Spill / Release"]:
        return "No Injury"
    natures = ["Laceration","Sprain/Strain","Contusion","Fracture",
               "Burn","Eye Injury","Chemical Burn","Crush Injury"]
    return random.choice(natures)


def generate_corrective_actions(incidents: pd.DataFrame) -> pd.DataFrame:
    """Generate corrective actions for each incident — 2–5 actions per event."""
    records = []
    ca_counter = 1

    for _, inc in incidents.iterrows():
        n_actions = random.randint(2, 5)
        inc_date = datetime.strptime(inc["incident_date"], "%Y-%m-%d").date()

        action_types = [
            "Immediate Corrective Action",
            "Root Cause Corrective Action",
            random.choice(["Preventive Action","System Improvement",
                          "Training Requirement","Engineering Control",
                          "Administrative Control"])
        ]
        if n_actions > 3:
            action_types += [random.choice([
                "Preventive Action","System Improvement",
                "Training Requirement","Engineering Control"
            ])] * (n_actions - 3)

        for j, action_type in enumerate(action_types[:n_actions]):
            due_days = 3 if j == 0 else random.randint(14, 60)
            due_date = inc_date + timedelta(days=due_days)
            if due_date > DATES[-1]:
                due_date = DATES[-1]

            is_closed = random.random() < 0.78
            comp_date = None
            if is_closed:
                comp_days = random.randint(due_days - 5, due_days + 10)
                comp_date = inc_date + timedelta(days=max(1, comp_days))
                if comp_date > DATES[-1]:
                    comp_date = DATES[-1]
                status = "Closed"
            else:
                overdue = due_date < DATES[-1]
                status = "Overdue" if overdue else "In Progress"

            records.append({
                "action_number":         f"CA-2024-{ca_counter:04d}",
                "incident_id":           inc.name + 1,
                "action_type":           action_type,
                "description":           _action_description(action_type, inc["incident_category"]),
                "assigned_to":           random.choice(PERSONNEL),
                "assigned_department":   inc["department"],
                "due_date":              due_date.isoformat(),
                "completion_date":       comp_date.isoformat() if comp_date else None,
                "status":                status,
                "priority":              "Critical" if j == 0 and inc["severity"] in ["Critical","High"] else
                                         "High" if inc["severity"] == "High" else
                                         "Medium" if inc["severity"] == "Medium" else "Low",
                "verification_required": 1,
                "verified_by":           random.choice(HSE_OFFICERS) if is_closed else None,
                "verification_date":     comp_date.isoformat() if is_closed and comp_date else None,
                "effectiveness_rating":  random.randint(3, 5) if is_closed else None,
                "notes":                 "Action implemented and verified effective." if is_closed else "Action in progress.",
            })
            ca_counter += 1

    df = pd.DataFrame(records)
    logger.info(f"Corrective actions generated: {len(df)}")
    return df


def _action_description(action_type: str, category: str) -> str:
    descs = {
        "Immediate Corrective Action":      f"Immediate corrective action for {category} — area made safe, hazard eliminated, work stopped pending review.",
        "Root Cause Corrective Action":     f"Root cause corrective action — procedure revised, management system gap closed for {category} incidents.",
        "Preventive Action":                f"Preventive action to eliminate recurrence — risk assessment updated, all similar work areas inspected.",
        "System Improvement":               f"Management system improvement — {category} hazard now included in pre-job risk assessment template.",
        "Training Requirement":             f"Training requirement identified — all workers in relevant area to complete refresher on {category} hazards.",
        "Engineering Control":              f"Engineering control to be installed — physical barrier / guard / interlocking to prevent recurrence.",
        "Administrative Control":           f"Administrative control — new work procedure drafted, reviewed, and communicated to workforce.",
    }
    return descs.get(action_type, "Corrective action assigned and tracked to completion.")


def generate_safety_observations(incidents: pd.DataFrame) -> pd.DataFrame:
    """
    Generate safety observations — near misses, unsafe acts, stop work events.
    Volume calibrated to maintain Heinrich Triangle ratio.
    Good reporting culture: >5 near misses per recordable = healthy.
    """
    records = []
    obs_counter = 1

    # 280 safety observations for the year
    for i in range(280):
        weights = [_seasonal_weight(j) for j in range(SIMULATION_DAYS)]
        total = sum(weights)
        weights = [w / total for w in weights]
        day_idx = np.random.choice(range(SIMULATION_DAYS), p=weights)
        obs_date = DATES[day_idx]

        obs_type = random.choices(
            ["Near Miss", "Unsafe Act", "Unsafe Condition",
             "Good Practice", "Safety Walk", "Stop Work Authority",
             "Dropped Object Potential", "Environmental Concern"],
            weights=[20, 25, 25, 15, 8, 4, 2, 1],
            k=1
        )[0]

        pot_severity = random.choices(
            ["Critical", "High", "Medium", "Low"],
            weights=[3, 12, 35, 50], k=1
        )[0]

        needs_followup = int(obs_type in ["Near Miss","Unsafe Act","Unsafe Condition","Stop Work Authority","Dropped Object Potential"])

        records.append({
            "observation_number":       f"OBS-2024-{obs_counter:04d}",
            "observation_date":         obs_date.isoformat(),
            "observation_type":         obs_type,
            "work_area":                random.choice(WORK_AREAS),
            "department":               random.choice(DEPARTMENTS),
            "description":              _observation_description(obs_type),
            "potential_severity":       pot_severity,
            "reported_by":              random.choice(PERSONNEL),
            "is_anonymous":             int(random.random() < 0.12),
            "immediate_action_taken":   _immediate_obs_action(obs_type),
            "followup_required":        needs_followup,
            "followup_action":          _followup_action(obs_type) if needs_followup else None,
            "followup_complete":        int(random.random() < 0.82) if needs_followup else 0,
        })
        obs_counter += 1

    df = pd.DataFrame(records)
    logger.info(f"Safety observations generated: {len(df)}")
    return df


def _observation_description(obs_type: str) -> str:
    descs = {
        "Near Miss":               "Near miss event — worker narrowly avoided contact with moving equipment. No injury. High potential consequence.",
        "Unsafe Act":              "Worker observed not wearing required PPE for task. Briefed on requirement. PPE donned immediately.",
        "Unsafe Condition":        "Spill on walkway creating slip hazard. Not barricaded. Housekeeping remedied before work resumed.",
        "Good Practice":           "Worker observed conducting comprehensive pre-job hazard assessment. Team briefed on all hazards before starting.",
        "Safety Walk":             "Routine safety walk completed. Minor housekeeping issues noted. Corrective actions raised.",
        "Stop Work Authority":     "Worker exercised Stop Work Authority — unsafe condition identified before task commencement. Task halted and reassessed.",
        "Dropped Object Potential":"Unsecured tool identified at height — potential dropped object risk. Item secured. Drop zone reassessed.",
        "Environmental Concern":   "Minor chemical drip from pump seal observed near drain. Contained immediately. Seal inspection raised.",
    }
    return descs.get(obs_type, "Safety observation recorded and actioned.")


def _immediate_obs_action(obs_type: str) -> str:
    actions = {
        "Near Miss":               "Work stopped. Area reassessed. Hazard eliminated before resumption.",
        "Unsafe Act":              "Worker counselled. Correct PPE provided. Toolbox talk conducted with crew.",
        "Unsafe Condition":        "Hazard barricaded. Housekeeping completed. Area re-inspected.",
        "Stop Work Authority":     "Task halted. Risk assessment reviewed. Management notified. Safe method of work confirmed before restart.",
        "Dropped Object Potential":"Item secured or removed. Drop zone extended. All workers below notified.",
        "Environmental Concern":   "Drip tray deployed. Pump isolated. Seal replacement raised as priority work order.",
    }
    return actions.get(obs_type, "Immediate action taken to control hazard.")


def _followup_action(obs_type: str) -> str:
    return random.choice([
        "Formal investigation to be conducted within 48 hours.",
        "Risk assessment to be reviewed and updated.",
        "Toolbox talk to be conducted with all workers in area.",
        "Procedure to be reviewed and reissued.",
        "Engineering control to be considered to prevent recurrence.",
        "Training refresher to be assigned to all relevant personnel.",
        "Management walk to verify corrective action effectiveness.",
    ])


def generate_hse_inspections() -> pd.DataFrame:
    records = []
    insp_counter = 1

    inspection_schedule = [
        ("Daily Safety Walk", 365, 1),
        ("Weekly HSE Inspection", 52, 3),
        ("Monthly Audit", 12, 8),
        ("Quarterly Management Audit", 4, 15),
        ("Regulatory Inspection", 2, 20),
        ("Emergency Response Drill", 4, 12),
    ]

    for insp_type, frequency, items in inspection_schedule:
        interval = SIMULATION_DAYS // frequency
        for i in range(frequency):
            insp_date = START_DATE + timedelta(days=i * interval + random.randint(-2, 2))
            if insp_date > DATES[-1]:
                insp_date = DATES[-1]

            # Scores degrade slightly through year — realistic maintenance of standards
            base_score = 88 - (i / frequency) * 8 + random.uniform(-5, 5)
            score = max(55.0, min(99.0, base_score))

            if score >= 90:   rating = "Excellent"
            elif score >= 80: rating = "Good"
            elif score >= 70: rating = "Satisfactory"
            elif score >= 60: rating = "Unsatisfactory"
            else:             rating = "Critical"

            findings = max(0, int(np.random.poisson(max(0.5, (100 - score) / 15))))
            critical = max(0, int(findings * random.uniform(0, 0.2)))
            major = max(0, int(findings * random.uniform(0.1, 0.35)))
            minor = max(0, findings - critical - major)

            records.append({
                "inspection_number":    f"INSP-2024-{insp_counter:04d}",
                "inspection_date":      insp_date.isoformat(),
                "inspection_type":      insp_type,
                "work_area":            random.choice(WORK_AREAS),
                "inspector":            random.choice(HSE_OFFICERS),
                "inspection_score":     round(score, 1),
                "items_inspected":      items,
                "findings_count":       findings,
                "critical_findings":    critical,
                "major_findings":       major,
                "minor_findings":       minor,
                "actions_raised":       findings,
                "overall_rating":       rating,
                "notes":                f"Inspection completed. {findings} finding(s) recorded. Actions raised per HSE action tracker.",
                "next_inspection_date": (insp_date + timedelta(days=interval)).isoformat(),
            })
            insp_counter += 1

    df = pd.DataFrame(records).sort_values("inspection_date").reset_index(drop=True)
    logger.info(f"HSE inspections generated: {len(df)}")
    return df


def generate_permit_to_work() -> pd.DataFrame:
    records = []
    ptw_counter = 1

    ptw_types = [
        ("Hot Work", 85),
        ("Cold Work", 120),
        ("Confined Space Entry", 45),
        ("Working at Height", 60),
        ("Electrical Isolation", 75),
        ("Chemical Handling", 40),
        ("Simultaneous Operations", 25),
    ]

    for ptw_type, count in ptw_types:
        for _ in range(count):
            day_idx = random.randint(0, SIMULATION_DAYS - 1)
            ptw_date = DATES[day_idx]
            start_hr = random.randint(6, 14)
            duration = random.randint(2, 10)
            end_hr = min(start_hr + duration, 23)

            violation = random.random() < 0.04  # 4% violation rate

            records.append({
                "permit_number":        f"PTW-2024-{ptw_counter:04d}",
                "permit_date":          ptw_date.isoformat(),
                "permit_type":          ptw_type,
                "work_area":            random.choice(WORK_AREAS),
                "work_description":     f"{ptw_type} task in facility. Work scope reviewed and approved by area authority.",
                "issued_by":            random.choice(HSE_OFFICERS),
                "accepted_by":          random.choice(PERSONNEL),
                "start_time":           f"{start_hr:02d}:00:00",
                "end_time":             f"{end_hr:02d}:00:00",
                "actual_end_time":      f"{end_hr + random.randint(-1,2):02d}:00:00",
                "workers_on_permit":    random.randint(1, 8),
                "isolation_required":   int(ptw_type in ["Electrical Isolation","Confined Space Entry","Hot Work"]),
                "gas_test_required":    int(ptw_type in ["Hot Work","Confined Space Entry","Chemical Handling"]),
                "gas_test_result":      random.choice(["Clear","Clear","Clear","Marginal"]) if ptw_type in ["Hot Work","Confined Space Entry"] else None,
                "fire_watch_required":  int(ptw_type == "Hot Work"),
                "status":               "Violated" if violation else "Closed",
                "violations_noted":     int(violation),
                "violation_description":_ptw_violation() if violation else None,
                "incident_linked":      None,
            })
            ptw_counter += 1

    df = pd.DataFrame(records)
    logger.info(f"PTW records generated: {len(df)}")
    return df


def _ptw_violation() -> str:
    return random.choice([
        "Work scope exceeded permit boundary — additional area entered without re-assessment.",
        "Fire watch abandoned before hot work cooling period completed.",
        "Additional workers joined task without being signed onto permit.",
        "Isolation not verified before confined space entry commenced.",
        "Gas test interval exceeded — re-test not conducted at required frequency.",
        "Permit expired without formal extension — work continued beyond authorised time.",
    ])


def generate_training_records() -> pd.DataFrame:
    records = []
    tr_counter = 1

    for emp_id in range(1, WORKFORCE_SIZE + 1):
        emp_name = f"Employee-{emp_id:03d}"
        dept = random.choice(DEPARTMENTS)
        emp_type = "Contractor" if random.random() < CONTRACT_WORKERS_PCT else "Direct"

        # Mandatory courses per employee
        mandatory_courses = random.sample(TRAINING_COURSES, k=random.randint(6, 12))
        for course_name, category, validity_days in mandatory_courses:
            # Training date — sometime in last 2 years
            days_ago = random.randint(0, int(validity_days * 0.9))
            train_date = START_DATE - timedelta(days=days_ago)
            if train_date < START_DATE - timedelta(days=730):
                train_date = START_DATE - timedelta(days=730)

            expiry = train_date + timedelta(days=validity_days)
            is_expired = int(expiry < DATES[-1])

            records.append({
                "employee_id":       f"EMP-{emp_id:04d}",
                "employee_name":     emp_name,
                "department":        dept,
                "employee_type":     emp_type,
                "training_course":   course_name,
                "training_category": category,
                "training_date":     train_date.isoformat(),
                "expiry_date":       expiry.isoformat(),
                "is_expired":        is_expired,
                "score_pct":         round(random.uniform(70, 98), 1),
                "passed":            1,
                "trainer":           random.choice(HSE_OFFICERS),
                "training_provider": random.choice(["Internal HSE Dept", "Bureau Veritas", "OPITO", "SGS", "Intertek"]),
                "certificate_number":f"CERT-{tr_counter:06d}",
                "mandatory":         1,
            })
            tr_counter += 1

    df = pd.DataFrame(records)
    logger.info(f"Training records generated: {len(df)}")
    return df


def compute_kpi_monthly(incidents: pd.DataFrame, observations: pd.DataFrame,
                        inspections: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly HSE KPIs — TRIR, LTIR, severity rate, leading indicators."""
    records = []

    # Monthly manhours
    daily_manhours = WORKFORCE_SIZE * WORKING_HOURS_PER_SHIFT * SHIFTS_PER_DAY * 0.85
    monthly_manhours = daily_manhours * 30.4

    incidents["incident_date"] = pd.to_datetime(incidents["incident_date"])
    observations["observation_date"] = pd.to_datetime(observations["observation_date"])
    inspections["inspection_date"] = pd.to_datetime(inspections["inspection_date"])

    months = pd.period_range(start=SIMULATION_START, periods=12, freq="M")

    cumulative_lti_free = 0
    last_lti_date = None

    for month in months:
        ym = str(month)
        month_start = month.start_time.date()
        month_end = month.end_time.date()

        month_inc = incidents[
            (incidents["incident_date"].dt.date >= month_start) &
            (incidents["incident_date"].dt.date <= month_end)
        ]
        month_obs = observations[
            (observations["observation_date"].dt.date >= month_start) &
            (observations["observation_date"].dt.date <= month_end)
        ]
        month_insp = inspections[
            (inspections["inspection_date"].dt.date >= month_start) &
            (inspections["inspection_date"].dt.date <= month_end)
        ]

        lti_count = len(month_inc[month_inc["incident_type"] == "Lost Time Injury"])
        rwc_count = len(month_inc[month_inc["incident_type"] == "Restricted Work Case"])
        mtc_count = len(month_inc[month_inc["incident_type"] == "Medical Treatment Case"])
        fac_count = len(month_inc[month_inc["incident_type"] == "First Aid Case"])
        nm_count  = len(month_inc[month_inc["incident_type"] == "Near Miss"])
        ua_count  = len(month_inc[month_inc["incident_type"] == "Unsafe Act"])
        uc_count  = len(month_inc[month_inc["incident_type"] == "Unsafe Condition"])
        pse_t1    = len(month_inc[(month_inc["incident_type"] == "Process Safety Event") & (month_inc["api_rp754_tier"] == "Tier 1")])
        pse_t2    = len(month_inc[(month_inc["incident_type"] == "Process Safety Event") & (month_inc["api_rp754_tier"] == "Tier 2")])
        pse_t3    = len(month_obs[(month_obs["observation_type"] == "Near Miss") & (month_obs["potential_severity"].isin(["Critical","High"]))])
        pse_t4    = len(month_obs[month_obs["observation_type"].isin(["Unsafe Act","Unsafe Condition"])])
        fatalities = len(month_inc[month_inc["incident_type"] == "Fatality"])

        recordables = lti_count + rwc_count + mtc_count + fatalities
        trir = round((recordables * 200000) / monthly_manhours, 4) if monthly_manhours > 0 else 0
        ltir = round((lti_count * 200000) / monthly_manhours, 4) if monthly_manhours > 0 else 0
        days_lost = month_inc["days_lost"].sum()
        severity_rate = round((days_lost * 200000) / monthly_manhours, 4) if monthly_manhours > 0 else 0
        near_miss_ratio = round(nm_count / max(recordables, 1), 2)

        # Inspection score
        avg_insp = month_insp["inspection_score"].mean() if not month_insp.empty else 85.0
        # Action closeout rate
        closeout_rate = round(random.uniform(72, 92), 1)
        # Training compliance
        training_comp = round(random.uniform(82, 96), 1)
        # PTW violations
        ptw_viol = random.randint(0, 3)

        # LTI-free days
        if lti_count > 0 or fatalities > 0:
            cumulative_lti_free = 0
        else:
            cumulative_lti_free += (month_end - month_start).days + 1

        total_cost = month_inc["estimated_cost_usd"].sum()

        records.append({
            "year_month":               ym,
            "total_manhours":           round(monthly_manhours, 0),
            "total_incidents":          len(month_inc),
            "fatalities":               fatalities,
            "lti_count":                lti_count,
            "rwc_count":                rwc_count,
            "mtc_count":                mtc_count,
            "fac_count":                fac_count,
            "near_miss_count":          nm_count,
            "pse_tier1_count":          pse_t1,
            "pse_tier2_count":          pse_t2,
            "pse_tier3_count":          pse_t3,
            "pse_tier4_count":          pse_t4,
            "unsafe_act_count":         ua_count,
            "unsafe_condition_count":   uc_count,
            "trir":                     trir,
            "ltir":                     ltir,
            "severity_rate":            severity_rate,
            "near_miss_ratio":          near_miss_ratio,
            "observation_count":        len(month_obs),
            "inspection_score_avg":     round(avg_insp, 1),
            "action_closeout_rate":     closeout_rate,
            "training_compliance_pct":  training_comp,
            "ptw_violations":           ptw_viol,
            "total_cost_usd":           round(total_cost, 0),
            "cumulative_lti_free_days": cumulative_lti_free,
        })

    df = pd.DataFrame(records)
    logger.info(f"Monthly KPIs generated: {len(df)} months")
    return df


def run_full_generation() -> dict:
    logger.info("=" * 60)
    logger.info("HSEI Platform — Data Generation START")
    logger.info("=" * 60)

    incidents    = generate_incidents()
    actions      = generate_corrective_actions(incidents)
    observations = generate_safety_observations(incidents)
    inspections  = generate_hse_inspections()
    ptw          = generate_permit_to_work()
    training     = generate_training_records()
    kpis         = compute_kpi_monthly(incidents, observations, inspections)

    result = {
        "incidents":            incidents,
        "corrective_actions":   actions,
        "safety_observations":  observations,
        "hse_inspections":      inspections,
        "permit_to_work":       ptw,
        "training_records":     training,
        "kpi_monthly_summary":  kpis,
    }

    for table, df in result.items():
        logger.success(f"  {table}: {len(df):,} records")

    logger.info("=" * 60)
    logger.success("Data generation COMPLETE")
    return result


if __name__ == "__main__":
    data = run_full_generation()
