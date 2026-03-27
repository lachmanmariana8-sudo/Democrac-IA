"""
DEMOCRAC.IA / PEIRS — Esquema SQLite
Tablas para persistir análisis, reportes, observaciones de campo y alertas.
"""

# DDL completo — ejecutar en orden (foreign keys respetadas)
SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Ejecuciones de análisis PEIRS ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analysis_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      TEXT    NOT NULL UNIQUE,          -- UUID generado en /api/analyze
    country_code TEXT   NOT NULL,                 -- ISO 3166-1 alpha-3
    election_date TEXT,                           -- ISO 8601 o NULL
    started_at  TEXT    NOT NULL,                 -- ISO 8601 UTC
    completed_at TEXT,                            -- NULL si aún en curso
    status      TEXT    NOT NULL DEFAULT 'running',  -- running | completed | failed
    risk_score  REAL,                             -- 0-100
    risk_level  TEXT,                             -- critical | high | moderate | low
    data_confidence TEXT,                         -- high | medium | low
    agent_version TEXT  DEFAULT 'v0.3',
    error_msg   TEXT                              -- NULL si no falló
);

-- ── Reportes generados ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       TEXT    NOT NULL REFERENCES analysis_runs(run_id) ON DELETE CASCADE,
    country_code TEXT    NOT NULL,
    report_md    TEXT    NOT NULL,                -- markdown completo
    report_json  TEXT,                            -- JSON estructurado (opcional)
    chapters     TEXT,                            -- JSON: {cap_id: texto}
    created_at   TEXT    NOT NULL,
    file_path    TEXT                             -- ruta en disco si se guardó
);

-- ── Sesiones de observación electoral ────────────────────────────────────
CREATE TABLE IF NOT EXISTS observation_sessions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT    NOT NULL UNIQUE,         -- UUID
    country_code TEXT    NOT NULL,
    phase        TEXT    NOT NULL DEFAULT 'pre_election',
    -- pre_election | campaign | election_day | counting | post_election
    started_at   TEXT    NOT NULL,
    ended_at     TEXT,
    status       TEXT    NOT NULL DEFAULT 'active',  -- active | closed
    total_entries INTEGER DEFAULT 0,
    pattern_score REAL,                           -- score de fraude sistémico (0-1)
    run_id       TEXT    REFERENCES analysis_runs(run_id)
);

-- ── Hallazgos de observadores de campo ───────────────────────────────────
CREATE TABLE IF NOT EXISTS observation_entries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id      TEXT    NOT NULL UNIQUE,        -- UUID
    session_id    TEXT    NOT NULL REFERENCES observation_sessions(session_id) ON DELETE CASCADE,
    country_code  TEXT    NOT NULL,

    -- Datos del hallazgo
    category      TEXT    NOT NULL,
    -- voter_intimidation | ballot_tampering | irregular_procedure | hate_speech
    -- disenfranchisement | fraud_allegation | violence | media_restriction | other
    severity      TEXT    NOT NULL DEFAULT 'medium',  -- low | medium | high | critical
    finding       TEXT    NOT NULL,               -- descripción del hallazgo
    location      TEXT,                           -- distrito / municipio / local
    observed_at   TEXT    NOT NULL,               -- ISO 8601 UTC (hora del evento)
    submitted_at  TEXT    NOT NULL,               -- ISO 8601 UTC (hora de envío)

    -- Validación (Agent 5)
    validated        INTEGER DEFAULT 0,           -- 0=pendiente, 1=válido, -1=rechazado
    quality_score    REAL,                        -- 0-1 (Agent 5)
    duplicate_of     TEXT,                        -- entry_id del duplicado detectado
    validation_notes TEXT,                        -- warnings del validador

    -- Evidencia
    has_evidence  INTEGER DEFAULT 0,
    evidence_desc TEXT,
    evidence_url  TEXT,

    -- Observador
    observer_id   TEXT,                           -- ID anónimo del observador
    observer_org  TEXT,                           -- organización observadora

    -- Trazabilidad
    confidence    TEXT    DEFAULT 'unverified',   -- confirmed | probable | unverified | mock
    iccpr_articles TEXT,                          -- JSON array de artículos violados
    cedaw_articles TEXT                           -- JSON array de artículos CEDAW
);

-- ── Patrones detectados por Agent 5 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS detection_patterns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT    NOT NULL REFERENCES observation_sessions(session_id) ON DELETE CASCADE,
    pattern_type TEXT    NOT NULL,
    -- geographic | category_cluster | temporal_escalation | multi_observer | fraud_systematic
    description  TEXT    NOT NULL,
    districts    TEXT,                            -- JSON array de distritos afectados
    entry_count  INTEGER DEFAULT 0,
    fraud_score  REAL    DEFAULT 0.0,             -- 0-1
    detected_at  TEXT    NOT NULL,
    is_escalated INTEGER DEFAULT 0               -- si ya se envió alerta
);

-- ── Alertas despachadas (Agent 7) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alerts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id     TEXT    NOT NULL UNIQUE,         -- UUID de deduplicación
    country_code TEXT    NOT NULL,
    event_type   TEXT    NOT NULL,
    -- critical_entry | fraud_pattern | escalation | corroboration | ooni_block
    severity     TEXT    NOT NULL,
    title        TEXT    NOT NULL,
    description  TEXT,
    entry_id     TEXT,                            -- entry_id que disparó la alerta
    session_id   TEXT,
    fraud_score  REAL,
    rights_at_risk TEXT,                          -- JSON array
    dispatched_at TEXT   NOT NULL,
    channels     TEXT,                            -- JSON: {slack: bool, webhook: bool, email: bool}
    channels_ok  INTEGER DEFAULT 0,              -- canales exitosos
    error_msg    TEXT                             -- NULL si OK
);

-- ── OONI snapshots ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ooni_snapshots (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT    NOT NULL,
    fetched_at   TEXT    NOT NULL,
    blocked_urls INTEGER DEFAULT 0,
    anomalies    INTEGER DEFAULT 0,
    summary_json TEXT,                            -- JSON completo del snapshot
    UNIQUE(country_code, fetched_at)
);

-- ── Índices para queries frecuentes ──────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_runs_country    ON analysis_runs(country_code, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_run     ON reports(run_id);
CREATE INDEX IF NOT EXISTS idx_entries_session ON observation_entries(session_id, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_entries_severity ON observation_entries(country_code, severity);
CREATE INDEX IF NOT EXISTS idx_alerts_country  ON alerts(country_code, dispatched_at DESC);
CREATE INDEX IF NOT EXISTS idx_ooni_country    ON ooni_snapshots(country_code, fetched_at DESC);
"""

# Versión del schema — incrementar al hacer cambios estructurales
SCHEMA_VERSION = 1
