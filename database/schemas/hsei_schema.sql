-- =============================================================================
-- HSEI Platform — Database Schema
-- Version: 1.0.0
-- Standards: API RP 754, ISO 45001, OSHA 29 CFR 1910.119, RIDDOR
-- Facility: Offshore Production Complex OPC-Alpha
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLE: incidents
-- Purpose: Master incident register — every HSE event recorded on the facility.
-- Standard alignment: OSHA 300 log fields, API RP 754 tier classification,
--   ISO 45001 incident investigation requirements.
-- HSE significance: Primary data source for TRIR, LTIR, severity trending,
--   causal analysis, and regulatory reporting.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incidents (
    id                      INTEGER     PRIMARY KEY AUTOINCREMENT,
    incident_number         VARCHAR(20) UNIQUE NOT NULL,
    incident_date           DATE        NOT NULL,
    incident_time           TIME,
    incident_type           VARCHAR(60) NOT NULL,
    incident_category       VARCHAR(80) NOT NULL,
    api_rp754_tier          VARCHAR(10),        -- Tier 1/2/3/4 (NULL for personal safety events)
    severity                VARCHAR(20) NOT NULL CHECK (severity IN ('Critical','High','Medium','Low','Negligible')),
    work_area               VARCHAR(80),
    department              VARCHAR(80),
    description             TEXT        NOT NULL,
    immediate_cause         TEXT,
    root_cause_category     VARCHAR(100),
    root_cause_description  TEXT,
    contributing_factors    TEXT,
    body_part_affected      VARCHAR(60),
    injury_nature           VARCHAR(60),        -- Fracture, Laceration, Burn, Sprain etc.
    days_lost               INTEGER     DEFAULT 0,
    days_restricted         INTEGER     DEFAULT 0,
    employee_type           VARCHAR(20) CHECK (employee_type IN ('Direct','Contractor','Visitor','Unknown')),
    workers_involved        INTEGER     DEFAULT 1,
    witnesses               INTEGER     DEFAULT 0,
    reported_by             VARCHAR(60),
    investigated_by         VARCHAR(60),
    investigation_complete  INTEGER     DEFAULT 0,
    regulatory_reportable   INTEGER     DEFAULT 0,
    reported_to_regulator   INTEGER     DEFAULT 0,
    regulator_reference     VARCHAR(40),
    estimated_cost_usd      REAL        DEFAULT 0,
    actual_cost_usd         REAL        DEFAULT 0,
    property_damage_usd     REAL        DEFAULT 0,
    environmental_impact    INTEGER     DEFAULT 0,  -- 1=Yes
    spill_volume_litres     REAL,
    is_recurring            INTEGER     DEFAULT 0,
    previous_similar_event  VARCHAR(20),
    closure_date            DATE,
    is_closed               INTEGER     DEFAULT 0,
    created_at              TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE: corrective_actions
-- Purpose: Tracks all corrective and preventive actions arising from incidents.
-- HSE significance: Action close-out rate is a leading indicator of HSE
--   management system effectiveness. Open actions signal systemic risk.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS corrective_actions (
    id                      INTEGER     PRIMARY KEY AUTOINCREMENT,
    action_number           VARCHAR(20) UNIQUE NOT NULL,
    incident_id             INTEGER,
    action_type             VARCHAR(40) NOT NULL CHECK (action_type IN (
                                'Immediate Corrective Action',
                                'Root Cause Corrective Action',
                                'Preventive Action',
                                'System Improvement',
                                'Training Requirement',
                                'Engineering Control',
                                'Administrative Control'
                            )),
    description             TEXT        NOT NULL,
    assigned_to             VARCHAR(60),
    assigned_department     VARCHAR(80),
    due_date                DATE,
    completion_date         DATE,
    status                  VARCHAR(20) NOT NULL DEFAULT 'Open' CHECK (status IN (
                                'Open','In Progress','Overdue','Closed','Cancelled'
                            )),
    priority                VARCHAR(10) CHECK (priority IN ('Critical','High','Medium','Low')),
    verification_required   INTEGER     DEFAULT 1,
    verified_by             VARCHAR(60),
    verification_date       DATE,
    effectiveness_rating    INTEGER,    -- 1-5 scale post-implementation review
    notes                   TEXT,
    created_at              TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE: safety_observations
-- Purpose: Near miss reports, safety walks, unsafe act/condition reports.
-- HSE significance: Near miss frequency is the strongest leading indicator
--   available. High near miss reporting = healthy reporting culture.
--   Heinrich's Triangle: For every fatality there are ~300 near misses.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS safety_observations (
    id                      INTEGER     PRIMARY KEY AUTOINCREMENT,
    observation_number      VARCHAR(20) UNIQUE NOT NULL,
    observation_date        DATE        NOT NULL,
    observation_type        VARCHAR(40) NOT NULL CHECK (observation_type IN (
                                'Near Miss',
                                'Unsafe Act',
                                'Unsafe Condition',
                                'Good Practice',
                                'Safety Walk',
                                'Stop Work Authority',
                                'Dropped Object Potential',
                                'Environmental Concern'
                            )),
    work_area               VARCHAR(80),
    department              VARCHAR(80),
    description             TEXT        NOT NULL,
    potential_severity      VARCHAR(20) CHECK (potential_severity IN ('Critical','High','Medium','Low')),
    reported_by             VARCHAR(60),
    is_anonymous            INTEGER     DEFAULT 0,
    immediate_action_taken  TEXT,
    followup_required       INTEGER     DEFAULT 0,
    followup_action         TEXT,
    followup_complete       INTEGER     DEFAULT 0,
    created_at              TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE: hse_inspections
-- Purpose: Formal HSE inspection and audit records.
-- HSE significance: Inspection scores track facility safety condition over time.
--   Declining scores precede incident clusters.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hse_inspections (
    id                      INTEGER     PRIMARY KEY AUTOINCREMENT,
    inspection_number       VARCHAR(20) UNIQUE NOT NULL,
    inspection_date         DATE        NOT NULL,
    inspection_type         VARCHAR(60) NOT NULL CHECK (inspection_type IN (
                                'Daily Safety Walk',
                                'Weekly HSE Inspection',
                                'Monthly Audit',
                                'Quarterly Management Audit',
                                'Regulatory Inspection',
                                'Third Party Audit',
                                'Pre-Job Safety Inspection',
                                'Emergency Response Drill'
                            )),
    work_area               VARCHAR(80),
    inspector               VARCHAR(60),
    inspection_score        REAL        CHECK (inspection_score BETWEEN 0 AND 100),
    items_inspected         INTEGER,
    findings_count          INTEGER     DEFAULT 0,
    critical_findings       INTEGER     DEFAULT 0,
    major_findings          INTEGER     DEFAULT 0,
    minor_findings          INTEGER     DEFAULT 0,
    actions_raised          INTEGER     DEFAULT 0,
    overall_rating          VARCHAR(20) CHECK (overall_rating IN (
                                'Excellent','Good','Satisfactory','Unsatisfactory','Critical'
                            )),
    notes                   TEXT,
    next_inspection_date    DATE,
    created_at              TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE: permit_to_work
-- Purpose: Permit To Work (PTW) system records.
-- HSE significance: PTW failures are a leading cause of major process
--   safety events in O&G. Tracking PTW violations and near misses
--   is a critical process safety leading indicator.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS permit_to_work (
    id                      INTEGER     PRIMARY KEY AUTOINCREMENT,
    permit_number           VARCHAR(20) UNIQUE NOT NULL,
    permit_date             DATE        NOT NULL,
    permit_type             VARCHAR(40) NOT NULL CHECK (permit_type IN (
                                'Hot Work',
                                'Cold Work',
                                'Confined Space Entry',
                                'Working at Height',
                                'Electrical Isolation',
                                'Excavation',
                                'Diving / Underwater',
                                'Radiography',
                                'Chemical Handling',
                                'Simultaneous Operations'
                            )),
    work_area               VARCHAR(80),
    work_description        TEXT,
    issued_by               VARCHAR(60),
    accepted_by             VARCHAR(60),
    start_time              TIME,
    end_time                TIME,
    actual_end_time         TIME,
    workers_on_permit       INTEGER,
    isolation_required      INTEGER     DEFAULT 0,
    gas_test_required       INTEGER     DEFAULT 0,
    gas_test_result         VARCHAR(20),
    fire_watch_required     INTEGER     DEFAULT 0,
    status                  VARCHAR(20) DEFAULT 'Closed' CHECK (status IN (
                                'Open','Suspended','Closed','Cancelled','Violated'
                            )),
    violations_noted        INTEGER     DEFAULT 0,
    violation_description   TEXT,
    incident_linked         INTEGER,
    created_at              TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE: training_records
-- Purpose: HSE training completion and competency records.
-- HSE significance: Training compliance is a mandatory regulatory requirement
--   and a leading indicator. Undertrained workforce = elevated incident risk.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS training_records (
    id                      INTEGER     PRIMARY KEY AUTOINCREMENT,
    employee_id             VARCHAR(20) NOT NULL,
    employee_name           VARCHAR(60) NOT NULL,
    department              VARCHAR(80),
    employee_type           VARCHAR(20),
    training_course         VARCHAR(100) NOT NULL,
    training_category       VARCHAR(60),
    training_date           DATE        NOT NULL,
    expiry_date             DATE,
    is_expired              INTEGER     DEFAULT 0,
    score_pct               REAL,
    passed                  INTEGER     DEFAULT 1,
    trainer                 VARCHAR(60),
    training_provider       VARCHAR(80),
    certificate_number      VARCHAR(40),
    mandatory               INTEGER     DEFAULT 1,
    created_at              TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE: kpi_monthly_summary
-- Purpose: Pre-computed monthly HSE KPI aggregations.
-- HSE significance: Industry-standard KPI reporting cadence for O&G operators.
--   Feeds executive dashboard and regulatory submissions.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kpi_monthly_summary (
    id                          INTEGER     PRIMARY KEY AUTOINCREMENT,
    year_month                  VARCHAR(7)  NOT NULL,   -- YYYY-MM
    total_manhours              REAL,
    total_incidents             INTEGER     DEFAULT 0,
    fatalities                  INTEGER     DEFAULT 0,
    lti_count                   INTEGER     DEFAULT 0,
    rwc_count                   INTEGER     DEFAULT 0,
    mtc_count                   INTEGER     DEFAULT 0,
    fac_count                   INTEGER     DEFAULT 0,
    near_miss_count             INTEGER     DEFAULT 0,
    pse_tier1_count             INTEGER     DEFAULT 0,
    pse_tier2_count             INTEGER     DEFAULT 0,
    pse_tier3_count             INTEGER     DEFAULT 0,
    pse_tier4_count             INTEGER     DEFAULT 0,
    unsafe_act_count            INTEGER     DEFAULT 0,
    unsafe_condition_count      INTEGER     DEFAULT 0,
    trir                        REAL,   -- Total Recordable Incident Rate
    ltir                        REAL,   -- Lost Time Incident Rate
    severity_rate               REAL,   -- Days lost per 200,000 manhours
    near_miss_ratio             REAL,   -- Near misses per recordable
    observation_count           INTEGER     DEFAULT 0,
    inspection_score_avg        REAL,
    action_closeout_rate        REAL,
    training_compliance_pct     REAL,
    ptw_violations              INTEGER     DEFAULT 0,
    total_cost_usd              REAL        DEFAULT 0,
    cumulative_lti_free_days    INTEGER     DEFAULT 0,
    created_at                  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year_month)
);

-- -----------------------------------------------------------------------------
-- INDEXES
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_inc_date        ON incidents(incident_date);
CREATE INDEX IF NOT EXISTS idx_inc_type        ON incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_inc_area        ON incidents(work_area);
CREATE INDEX IF NOT EXISTS idx_ca_incident     ON corrective_actions(incident_id);
CREATE INDEX IF NOT EXISTS idx_ca_status       ON corrective_actions(status);
CREATE INDEX IF NOT EXISTS idx_obs_date        ON safety_observations(observation_date);
CREATE INDEX IF NOT EXISTS idx_insp_date       ON hse_inspections(inspection_date);
CREATE INDEX IF NOT EXISTS idx_ptw_date        ON permit_to_work(permit_date);
CREATE INDEX IF NOT EXISTS idx_kpi_month       ON kpi_monthly_summary(year_month);

-- -----------------------------------------------------------------------------
-- VIEWS
-- -----------------------------------------------------------------------------

-- Current open corrective actions requiring attention
CREATE VIEW IF NOT EXISTS vw_open_actions AS
SELECT
    ca.action_number,
    ca.incident_id,
    i.incident_number,
    i.incident_type,
    ca.action_type,
    ca.description,
    ca.assigned_to,
    ca.assigned_department,
    ca.due_date,
    ca.priority,
    ca.status,
    CAST(julianday('now') - julianday(ca.due_date) AS INTEGER) AS days_overdue
FROM corrective_actions ca
LEFT JOIN incidents i ON ca.incident_id = i.id
WHERE ca.status IN ('Open','In Progress','Overdue')
ORDER BY ca.priority, ca.due_date;

-- Incident Pareto by category
CREATE VIEW IF NOT EXISTS vw_incident_pareto AS
SELECT
    incident_category,
    COUNT(*)                                                AS incident_count,
    SUM(days_lost)                                         AS total_days_lost,
    SUM(estimated_cost_usd)                                AS total_cost_usd,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)    AS pct_of_total
FROM incidents
GROUP BY incident_category
ORDER BY incident_count DESC;

-- Heinrich Triangle leading/lagging ratio
CREATE VIEW IF NOT EXISTS vw_heinrich_triangle AS
SELECT
    strftime('%Y-%m', incident_date)     AS year_month,
    COUNT(CASE WHEN incident_type = 'Fatality'              THEN 1 END) AS fatalities,
    COUNT(CASE WHEN incident_type = 'Lost Time Injury'      THEN 1 END) AS ltis,
    COUNT(CASE WHEN incident_type IN ('Restricted Work Case','Medical Treatment Case') THEN 1 END) AS recordables,
    COUNT(CASE WHEN incident_type = 'First Aid Case'        THEN 1 END) AS first_aids,
    COUNT(CASE WHEN incident_type = 'Near Miss'             THEN 1 END) AS near_misses,
    COUNT(CASE WHEN incident_type IN ('Unsafe Act','Unsafe Condition') THEN 1 END) AS unsafe_conditions
FROM incidents
GROUP BY strftime('%Y-%m', incident_date)
ORDER BY year_month;
