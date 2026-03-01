"""
Utility script to drop all demo_* tables from the Retool PostgreSQL database.

Use this when the older demo tables (demo_companies, demo_people, etc.)
or the newer simple demo tables (demo_threads, demo_emails) are no longer needed.

Run:
    python drop_demo_tables.py
"""
from retool_db_manager import RetoolDBManager


def drop_demo_tables():
    db = RetoolDBManager()

    if not db.connect():
        print("[ERROR] Failed to connect to database")
        return

    # Explicit list of known demo_* tables, ordered so dependent tables are dropped first
    demo_tables = [
        "demo_interaction_participants",
        "demo_person_expertise",
        "demo_processed_emails",
        "demo_interactions",
        "demo_expertise_areas",
        "demo_people",
        "demo_companies",
        "demo_emails",
        "demo_threads",
    ]

    try:
        print("Dropping demo_* tables (if they exist):")
        for name in demo_tables:
            print(f"  - {name}")
            db.execute_query(f'DROP TABLE IF EXISTS "{name}" CASCADE;', fetch=False)

        print("\n[SUCCESS] Requested demo_* tables have been dropped (or did not exist).")

    except Exception as e:
        print(f"[ERROR] Failed to drop demo tables: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    drop_demo_tables()

