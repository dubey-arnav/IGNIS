-- Enable PostGIS for spatial queries and geometry indexing
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. NASA FIRMS Thermal Events
CREATE TABLE IF NOT EXISTS thermal_events (
    id              SERIAL PRIMARY KEY,
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    geom            GEOMETRY(Point, 4326) NOT NULL,
    event_date      DATE NOT NULL,
    event_time      TIME,
    satellite       VARCHAR(20),
    instrument      VARCHAR(20),
    confidence      VARCHAR(10),
    bright_ti4      DOUBLE PRECISION,
    bright_ti5      DOUBLE PRECISION,
    frp             DOUBLE PRECISION,
    daynight        VARCHAR(1),
    source          VARCHAR(20) DEFAULT 'FIRMS',
    cluster_id      INTEGER,
    firms_uid       TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_thermal_events_geom
    ON thermal_events USING GIST (geom);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_thermal_events_firms_uid'
    ) THEN
        ALTER TABLE thermal_events ADD CONSTRAINT uq_thermal_events_firms_uid UNIQUE (firms_uid);
    END IF;
END $$;

-- 2. OpenStreetMap Industrial Infrastructure
CREATE TABLE IF NOT EXISTS industrial_sites (
    id              SERIAL PRIMARY KEY,
    osm_id          BIGINT,
    name            VARCHAR(255),
    type            VARCHAR(100),
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    geom            GEOMETRY(Point, 4326) NOT NULL,
    tags            JSONB,
    source          VARCHAR(20) DEFAULT 'OSM',
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_industrial_sites_geom
    ON industrial_sites USING GIST (geom);

-- 3. Aggregated Fire Clusters
CREATE TABLE IF NOT EXISTS fire_clusters (
    id                  SERIAL PRIMARY KEY,
    geom                GEOMETRY(Point, 4326) NOT NULL,
    first_detection     DATE,
    last_detection      DATE,
    total_detections    INTEGER,
    active_days         INTEGER,
    mean_frp            DOUBLE PRECISION,
    max_frp             DOUBLE PRECISION,
    persistence_score   DOUBLE PRECISION,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fire_clusters_geom
    ON fire_clusters USING GIST (geom);

-- 4. Machine Learning Risk Scores
CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES thermal_events(id),
    cluster_id INTEGER REFERENCES fire_clusters(id),
    predicted_label VARCHAR(50) NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_tier VARCHAR(10) NOT NULL,
    model_version VARCHAR(50),
    scored_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_risk_scores_event_id UNIQUE (event_id)
);

CREATE INDEX IF NOT EXISTS idx_risk_scores_tier
    ON risk_scores(risk_tier);
