# database/sync_to_supabase.py
"""
Synchronizes local PostgreSQL data (IGNIS) directly to your remote Supabase PostgreSQL database.
Uses high-performance bulk operations (execute_values) for fast data transfer.
Transfers:
1. industrial_sites (31,900 rows)
2. fire_clusters (1,832 rows)
3. thermal_events (12,155 rows)
4. risk_scores (12,155 rows)

Usage:
  python database/sync_to_supabase.py --target "postgresql://postgres.xxx:password@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require"
"""
import os
import sys
import json
import argparse
import logging
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ignis.sync_supabase")

LOCAL_USER = os.getenv("DB_USER", "postgres")
LOCAL_PASS = os.getenv("DB_PASSWORD", "admin")
LOCAL_HOST = os.getenv("DB_HOST", "localhost")
LOCAL_PORT = os.getenv("DB_PORT", "5432")
LOCAL_DB = os.getenv("DB_NAME", "IGNIS")


def get_local_conn():
    return psycopg2.connect(
        dbname=LOCAL_DB,
        user=LOCAL_USER,
        password=LOCAL_PASS,
        host=LOCAL_HOST,
        port=LOCAL_PORT,
    )


def sync_table(local_cur, remote_cur, table_name, select_sql, insert_sql, template, transform_fn=None, batch_size=2500):
    remote_cur.execute(f"SELECT COUNT(*) FROM {table_name};")
    remote_count = remote_cur.fetchone()[0]
    if remote_count > 0:
        logger.info(f"Table '{table_name}' on remote already has {remote_count} records. Skipping.")
        return

    local_cur.execute(f"SELECT COUNT(*) FROM {table_name};")
    total_rows = local_cur.fetchone()[0]
    logger.info(f"Syncing {total_rows} rows for table '{table_name}'...")

    local_cur.execute(select_sql)
    transferred = 0

    while True:
        rows = local_cur.fetchmany(batch_size)
        if not rows:
            break
        if transform_fn:
            rows = [transform_fn(r) for r in rows]

        execute_values(remote_cur, insert_sql, rows, template=template, page_size=batch_size)
        transferred += len(rows)
        logger.info(f"  [{table_name}] Progress: {transferred}/{total_rows} rows inserted")

    logger.info(f"Finished syncing '{table_name}'. Total: {transferred} rows.")


def sync(target_url: str):
    logger.info("Connecting to Local PostgreSQL...")
    local_conn = get_local_conn()
    local_cur = local_conn.cursor()

    logger.info("Connecting to Remote Supabase PostgreSQL...")
    if "sslmode" not in target_url and "?" not in target_url:
        target_url += "?sslmode=require"
    remote_conn = psycopg2.connect(target_url)
    remote_cur = remote_conn.cursor()

    # 1. Enable PostGIS
    logger.info("Verifying PostGIS on remote...")
    remote_cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    remote_conn.commit()

    # 2. Ensure Schema
    init_sql_path = os.path.join(os.path.dirname(__file__), "init.sql")
    if os.path.exists(init_sql_path):
        with open(init_sql_path, "r", encoding="utf-8") as f:
            sql_statements = f.read()
        logger.info("Ensuring schema tables and indexes exist on remote...")
        remote_cur.execute(sql_statements)
        remote_conn.commit()

    # 3. Table 1: industrial_sites
    def transform_industrial(r):
        (id_, osm_id, name, type_, lat, lon, tags, source, created_at) = r
        tags_str = json.dumps(tags) if isinstance(tags, (dict, list)) else tags
        return (id_, osm_id, name, type_, lat, lon, tags_str, source, created_at, lon, lat)

    sync_table(
        local_cur=local_cur,
        remote_cur=remote_cur,
        table_name="industrial_sites",
        select_sql="SELECT id, osm_id, name, type, latitude, longitude, tags, source, created_at FROM industrial_sites ORDER BY id",
        insert_sql="""
            INSERT INTO industrial_sites 
                (id, osm_id, name, type, latitude, longitude, tags, source, created_at, geom) 
            VALUES %s 
            ON CONFLICT DO NOTHING
        """,
        template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
        transform_fn=transform_industrial,
        batch_size=3000,
    )
    remote_conn.commit()

    # 4. Table 2: fire_clusters
    sync_table(
        local_cur=local_cur,
        remote_cur=remote_cur,
        table_name="fire_clusters",
        select_sql="""
            SELECT id, ST_AsText(geom), first_detection, last_detection, 
                   total_detections, active_days, mean_frp, max_frp, persistence_score, created_at 
            FROM fire_clusters ORDER BY id
        """,
        insert_sql="""
            INSERT INTO fire_clusters 
                (id, geom, first_detection, last_detection, total_detections, active_days, mean_frp, max_frp, persistence_score, created_at) 
            VALUES %s 
            ON CONFLICT DO NOTHING
        """,
        template="(%s, ST_SetSRID(ST_GeomFromText(%s), 4326), %s, %s, %s, %s, %s, %s, %s, %s)",
        batch_size=3000,
    )
    remote_conn.commit()

    # 5. Table 3: thermal_events
    def transform_thermal(r):
        (id_, lat, lon, ev_date, ev_time, sat, inst, conf, b4, b5, frp, dn, src, cl_id, f_uid, created_at) = r
        return (id_, lat, lon, ev_date, ev_time, sat, inst, conf, b4, b5, frp, dn, src, cl_id, f_uid, created_at, lon, lat)

    sync_table(
        local_cur=local_cur,
        remote_cur=remote_cur,
        table_name="thermal_events",
        select_sql="""
            SELECT id, latitude, longitude, event_date, event_time, satellite, instrument, 
                   confidence, bright_ti4, bright_ti5, frp, daynight, source, cluster_id, firms_uid, created_at 
            FROM thermal_events ORDER BY id
        """,
        insert_sql="""
            INSERT INTO thermal_events 
                (id, latitude, longitude, event_date, event_time, satellite, instrument, 
                 confidence, bright_ti4, bright_ti5, frp, daynight, source, cluster_id, firms_uid, created_at, geom) 
            VALUES %s 
            ON CONFLICT DO NOTHING
        """,
        template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
        transform_fn=transform_thermal,
        batch_size=3000,
    )
    remote_conn.commit()

    # 6. Table 4: risk_scores
    sync_table(
        local_cur=local_cur,
        remote_cur=remote_cur,
        table_name="risk_scores",
        select_sql="""
            SELECT id, event_id, cluster_id, predicted_label, risk_score, risk_tier, model_version, scored_at 
            FROM risk_scores ORDER BY id
        """,
        insert_sql="""
            INSERT INTO risk_scores 
                (id, event_id, cluster_id, predicted_label, risk_score, risk_tier, model_version, scored_at) 
            VALUES %s 
            ON CONFLICT DO NOTHING
        """,
        template="(%s, %s, %s, %s, %s, %s, %s, %s)",
        batch_size=3000,
    )
    remote_conn.commit()

    # Clean up
    local_cur.close()
    local_conn.close()
    remote_cur.close()
    remote_conn.close()
    logger.info("=== All data successfully synced to Supabase! ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync local IGNIS DB to remote Supabase DB.")
    parser.add_argument("--target", default=os.getenv("SUPABASE_DB_URL"), help="Supabase connection URL")
    args = parser.parse_args()

    if not args.target:
        print("ERROR: Please provide --target <SUPABASE_DB_URL> or set SUPABASE_DB_URL in your .env file.")
        sys.exit(1)

    sync(args.target)
