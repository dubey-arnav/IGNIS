  -- Enable PostGIS in case this file is run on a fresh database
  CREATE EXTENSION IF NOT EXISTS postgis;

  -- Thermal detections from NASA FIRMS
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
      created_at      TIMESTAMP DEFAULT NOW()
  );

  -- Spatial index so location-based queries (e.g. "find points within X km") are fast
  CREATE INDEX IF NOT EXISTS idx_thermal_events_geom
      ON thermal_events
      USING GIST (geom);

  -- Industrial infrastructure from OpenStreetMap
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
      ON industrial_sites
      USING GIST (geom);

  -- Groups of repeated detections believed to come from the same physical source
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
      ON fire_clusters
      USING GIST (geom);