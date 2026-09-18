# automation/steps/db_writer.py
import logging
from sqlalchemy import text

logger = logging.getLogger("ignis.automation.db_writer")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES thermal_events(id),
    cluster_id INTEGER REFERENCES fire_clusters(id),
    predicted_label VARCHAR(50) NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_tier VARCHAR(10) NOT NULL,
    model_version VARCHAR(50),
    scored_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (event_id)
);
"""


def ensure_schema(engine):
    """
    Ensures that risk_scores table exists and has a unique constraint on event_id
    so that ON CONFLICT (event_id) DO UPDATE works without error.
    """
    with engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'uq_risk_scores_event_id'
                ) THEN
                    DROP INDEX IF EXISTS idx_risk_scores_event_id;
                    ALTER TABLE risk_scores ADD CONSTRAINT uq_risk_scores_event_id UNIQUE (event_id);
                END IF;
            END $$;
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_risk_scores_tier ON risk_scores(risk_tier);"))



def upsert_risk_score(
    engine,
    event_id: int,
    cluster_id: int | None,
    result: dict,
    model_version: str = "xgb_v1",
):
    """
    Idempotently upsert predicted label and risk score into risk_scores table.
    """
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO risk_scores (event_id, cluster_id, predicted_label,
                                         risk_score, risk_tier, model_version)
                VALUES (:event_id, :cluster_id, :predicted_label,
                        :risk_score, :risk_tier, :model_version)
                ON CONFLICT (event_id) DO UPDATE SET
                    cluster_id = EXCLUDED.cluster_id,
                    predicted_label = EXCLUDED.predicted_label,
                    risk_score = EXCLUDED.risk_score,
                    risk_tier = EXCLUDED.risk_tier,
                    model_version = EXCLUDED.model_version,
                    scored_at = NOW()
            """),
            {
                "event_id": event_id,
                "cluster_id": cluster_id,
                "predicted_label": result["predicted_label"],
                "risk_score": float(result["risk_score"]),
                "risk_tier": result["risk_tier"],
                "model_version": model_version,
            },
        )
