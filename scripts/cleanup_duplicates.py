#!/usr/bin/env python3
"""Cleanup duplicate restaurantes safely.

Usage:
  # dry-run (default)
  python3 scripts/cleanup_duplicates.py

  # to actually apply changes (destructive!)
  python3 scripts/cleanup_duplicates.py --apply

This script finds restaurantes with the same `nombre`, shows the groups,
and when run with --apply it will:
 - reassign platos.restaurante_id and reservas.restaurante_id to the smallest id (keep_id)
 - delete the duplicate restaurante rows (keeping keep_id)

Run on development first and take a backup before applying in production.
"""

import os
import argparse
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "reserva"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password123"),
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}


def get_duplicate_restaurants(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
        SELECT nombre, array_agg(id ORDER BY id) AS ids, min(id) AS keep_id, count(*) as cnt
        FROM restaurantes
        GROUP BY nombre
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        """
        )
        return cur.fetchall()


def plan_for_group(group):
    nombre = group["nombre"]
    ids = group["ids"]
    keep_id = group["keep_id"]
    remove_ids = [i for i in ids if i != keep_id]
    return nombre, keep_id, remove_ids


def apply_group_fix(conn, nombre, keep_id, remove_ids):
    with conn.cursor() as cur:
        # Reassign platos
        cur.execute(
            "UPDATE platos SET restaurante_id = %s WHERE restaurante_id = ANY(%s)", (keep_id, remove_ids)
        )
        # Reassign reservas
        cur.execute(
            "UPDATE reservas SET restaurante_id = %s WHERE restaurante_id = ANY(%s)", (keep_id, remove_ids)
        )
        # Delete duplicate restaurantes
        cur.execute("DELETE FROM restaurantes WHERE id = ANY(%s)", (remove_ids,))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes (destructive). By default runs as dry-run")
    args = parser.parse_args()

    logger.info("Connecting to DB %s@%s:%s/%s", DB_CONFIG["user"], DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["dbname"])
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        dup = get_duplicate_restaurants(conn)
        if not dup:
            logger.info("No duplicate restaurantes found")
            return 0

        logger.info("Found %d duplicate restaurant groups", len(dup))
        for g in dup:
            nombre, keep_id, remove_ids = plan_for_group(g)
            logger.info("Group: %s -> keep_id=%s remove=%s", nombre, keep_id, remove_ids)
            if not args.apply:
                logger.info("DRY-RUN: would reassign platos/reservas to %s and delete %s", keep_id, remove_ids)
            else:
                logger.info("Applying for group '%s'", nombre)
                try:
                    apply_group_fix(conn, nombre, keep_id, remove_ids)
                    conn.commit()
                    logger.info("Applied: reassigned and deleted %s", remove_ids)
                except Exception as e:
                    conn.rollback()
                    logger.error("Failed to apply for %s: %s", nombre, e)

        if not args.apply:
            logger.info("Dry-run complete. To actually remove duplicates re-run with --apply (make DB backup first)")
        else:
            logger.info("All groups processed")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
