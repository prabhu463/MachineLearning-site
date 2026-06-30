-- PredictiveOps AI — Canonical Schema Reference
-- This file documents the authoritative schema.
-- Actual migrations are managed by Alembic (alembic/versions/).
-- To apply: alembic upgrade head
-- To rollback: alembic downgrade -1

-- ── Core monitoring tables ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS metrics (
    id              INTEGER PRIMARY KEY,
    service_name    VARCHAR(120)    NOT NULL,
    cpu_usage       DOUBLE PRECISION NOT NULL,
    memory_usage    DOUBLE PRECISION NOT NULL,
    disk_usage      DOUBLE PRECISION NOT NULL,
    network_latency_ms DOUBLE PRECISION NOT NULL,
    request_count   INTEGER         NOT NULL,
    error_rate      DOUBLE PRECISION NOT NULL,
    response_time_ms DOUBLE PRECISION NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_metrics_service_name    ON metrics (service_name);
CREATE INDEX IF NOT EXISTS ix_metrics_created_at      ON metrics (created_at);
CREATE INDEX IF NOT EXISTS ix_metrics_service_created ON metrics (service_name, created_at);

CREATE TABLE IF NOT EXISTS incidents (
    id              INTEGER PRIMARY KEY,
    metric_id       INTEGER         NOT NULL REFERENCES metrics(id) ON DELETE CASCADE,
    severity        VARCHAR(20)     NOT NULL,
    risk_score      DOUBLE PRECISION NOT NULL,
    predicted_label VARCHAR(32)     NOT NULL,
    root_cause      TEXT            NOT NULL,
    recommendation  TEXT            NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'open',
    notes           TEXT            NOT NULL DEFAULT '',
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_incidents_severity         ON incidents (severity);
CREATE INDEX IF NOT EXISTS ix_incidents_status           ON incidents (status);
CREATE INDEX IF NOT EXISTS ix_incidents_metric_id        ON incidents (metric_id);
CREATE INDEX IF NOT EXISTS ix_incidents_created_at       ON incidents (created_at);
CREATE INDEX IF NOT EXISTS ix_incidents_status_severity  ON incidents (status, severity);
CREATE INDEX IF NOT EXISTS ix_incidents_created_status   ON incidents (created_at, status);

CREATE TABLE IF NOT EXISTS action_events (
    id          INTEGER PRIMARY KEY,
    incident_id INTEGER         NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    action_name VARCHAR(120)    NOT NULL,
    executed_by VARCHAR(120)    NOT NULL,
    status      VARCHAR(30)     NOT NULL DEFAULT 'scheduled',
    details     TEXT            NOT NULL DEFAULT '',
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_action_events_incident_id ON action_events (incident_id);
CREATE INDEX IF NOT EXISTS ix_action_events_created_at  ON action_events (created_at);

CREATE TABLE IF NOT EXISTS model_registry (
    id              INTEGER PRIMARY KEY,
    model_name      VARCHAR(120)    NOT NULL,
    model_version   VARCHAR(40)     NOT NULL,
    artifact_path   VARCHAR(512)    NOT NULL,
    metrics_json    TEXT            NOT NULL DEFAULT '{}',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_model_registry_model_name ON model_registry (model_name);
CREATE INDEX IF NOT EXISTS ix_model_registry_created_at ON model_registry (created_at);

-- ── Auth & access control ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    username        VARCHAR(80)     NOT NULL UNIQUE,
    hashed_password VARCHAR(255)    NOT NULL,
    full_name       VARCHAR(160)    NOT NULL DEFAULT '',
    role            VARCHAR(20)     NOT NULL DEFAULT 'viewer',  -- admin | operator | viewer
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_users_email       ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_username    ON users (username);
CREATE INDEX IF NOT EXISTS ix_users_role        ON users (role);
CREATE INDEX IF NOT EXISTS ix_users_role_active ON users (role, is_active);

-- ── Alert rules ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS alerts (
    id              INTEGER PRIMARY KEY,
    name            VARCHAR(120)    NOT NULL,
    description     TEXT            NOT NULL DEFAULT '',
    metric_field    VARCHAR(80)     NOT NULL,       -- e.g. cpu_usage, error_rate
    operator        VARCHAR(10)     NOT NULL,       -- gt | lt | gte | lte
    threshold_value DOUBLE PRECISION NOT NULL,
    severity        VARCHAR(20)     NOT NULL DEFAULT 'warning',
    channel         VARCHAR(30)     NOT NULL DEFAULT 'none',   -- email | slack | webhook | none
    channel_target  VARCHAR(255)    NOT NULL DEFAULT '',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_fired_at   TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_alerts_metric_field   ON alerts (metric_field);
CREATE INDEX IF NOT EXISTS ix_alerts_active_field   ON alerts (is_active, metric_field);

-- ── Alembic version tracking ────────────────────────────────────────────────
-- Managed automatically by Alembic — do not edit manually.
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);
