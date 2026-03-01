"""
Build simple people + relationships tables from the raw demo_emails/demo_threads data.

Goal:
- Start from the clean raw model (demo_emails + demo_threads).
- Extract all unique email addresses into a simple people table.
- Build an undirected relationships table: "these two people have emailed in the same message".

This does NOT use any AI logic – it's just structure:
- who exists (people)
- who has interacted with whom (relationships) and how often.

Run:
    python build_people_and_relationships.py
"""

from datetime import datetime
from email.utils import getaddresses
from typing import Dict, List, Tuple, Set, Optional

from retool_db_manager import RetoolDBManager


def ensure_core_tables(db: RetoolDBManager) -> None:
    """Create simple core tables if they don't exist yet."""
    # People: one row per unique email address
    db.execute_query(
        """
        CREATE TABLE IF NOT EXISTS people (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255),
            first_seen TIMESTAMP,
            last_seen TIMESTAMP
        );
        """,
        fetch=False,
    )

    # Relationships: undirected edge between two people who appear in the same email
    db.execute_query(
        """
        CREATE TABLE IF NOT EXISTS relationships (
            id SERIAL PRIMARY KEY,
            person_a_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            person_b_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            message_count INTEGER NOT NULL DEFAULT 0,
            first_interaction TIMESTAMP,
            last_interaction TIMESTAMP,
            UNIQUE (person_a_id, person_b_id)
        );
        """,
        fetch=False,
    )


def parse_participants(row: Dict) -> Tuple[Set[str], Optional[datetime]]:
    """
    Parse all participants for an email row into a set of clean email addresses.
    Returns (set_of_emails, sent_at_datetime).
    """
    fields = []
    for key in ("from_email", "to_emails", "cc_emails", "bcc_emails"):
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            fields.append(val)

    addresses = getaddresses(fields)
    emails: Set[str] = set()
    for _name, addr in addresses:
        addr = (addr or "").strip()
        if "@" in addr:
            emails.add(addr.lower())

    sent_at = row.get("sent_at")
    # sent_at already comes from demo_emails as TIMESTAMP; keep as-is
    return emails, sent_at


def upsert_person(db: RetoolDBManager, email: str, sent_at: Optional[datetime]) -> int:
    """Create or update a person row and return its id."""
    # Best-effort name from email local-part
    local_part = email.split("@", 1)[0]
    default_name = local_part.replace(".", " ").title()

    # Insert or update name / first_seen / last_seen
    db.execute_query(
        """
        INSERT INTO people (email, name, first_seen, last_seen)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE
        SET
            name = COALESCE(people.name, EXCLUDED.name),
            first_seen = LEAST(
                COALESCE(people.first_seen, EXCLUDED.first_seen),
                COALESCE(EXCLUDED.first_seen, people.first_seen)
            ),
            last_seen = GREATEST(
                COALESCE(people.last_seen, EXCLUDED.last_seen),
                COALESCE(EXCLUDED.last_seen, people.last_seen)
            );
        """,
        (email, default_name, sent_at, sent_at),
        fetch=False,
    )

    # Fetch id
    row = db.execute_query(
        "SELECT id FROM people WHERE email = %s;",
        (email,),
        fetch=True,
    )[0]
    return row["id"]


def upsert_relationship(
    db: RetoolDBManager,
    person_a_id: int,
    person_b_id: int,
    sent_at: Optional[datetime],
) -> None:
    """Create or update an undirected relationship edge between two people."""
    if person_a_id == person_b_id:
        return

    # Enforce ordering so (a,b) and (b,a) collapse to one edge
    a, b = sorted((person_a_id, person_b_id))

    db.execute_query(
        """
        INSERT INTO relationships (
            person_a_id,
            person_b_id,
            message_count,
            first_interaction,
            last_interaction
        )
        VALUES (%s, %s, 1, %s, %s)
        ON CONFLICT (person_a_id, person_b_id) DO UPDATE
        SET
            message_count = relationships.message_count + 1,
            first_interaction = LEAST(
                COALESCE(relationships.first_interaction, EXCLUDED.first_interaction),
                COALESCE(EXCLUDED.first_interaction, relationships.first_interaction)
            ),
            last_interaction = GREATEST(
                COALESCE(relationships.last_interaction, EXCLUDED.last_interaction),
                COALESCE(EXCLUDED.last_interaction, relationships.last_interaction)
            );
        """,
        (a, b, sent_at, sent_at),
        fetch=False,
    )


def build_from_demo_emails():
    """Main entry: scan demo_emails and build people + relationships."""
    db = RetoolDBManager()

    if not db.connect():
        print("[ERROR] Failed to connect to database")
        return

    try:
        ensure_core_tables(db)

        # Pull all emails from the raw table
        rows = db.execute_query(
            """
            SELECT
                gmail_id,
                thread_id,
                from_email,
                to_emails,
                cc_emails,
                bcc_emails,
                sent_at
            FROM demo_emails;
            """,
            fetch=True,
        )

        print(f"Loaded {len(rows)} emails from demo_emails")

        person_cache: Dict[str, int] = {}
        processed_emails = 0
        skipped_emails = 0

        for i, row in enumerate(rows, start=1):
            participants, sent_at = parse_participants(row)

            if len(participants) < 2:
                skipped_emails += 1
                continue

            # Ensure all participants exist in people
            person_ids: Dict[str, int] = {}
            for email in participants:
                if email in person_cache:
                    pid = person_cache[email]
                else:
                    pid = upsert_person(db, email, sent_at)
                    person_cache[email] = pid
                person_ids[email] = pid

            # For this email, connect every pair of participants
            ids_list = list(person_ids.values())
            for idx_a in range(len(ids_list)):
                for idx_b in range(idx_a + 1, len(ids_list)):
                    upsert_relationship(db, ids_list[idx_a], ids_list[idx_b], sent_at)

            processed_emails += 1

            if i % 100 == 0:
                print(f"Processed {i}/{len(rows)} emails...")

        print("\nDone building people & relationships.")
        print(f"  Emails with >=2 participants: {processed_emails}")
        print(f"  Emails skipped (only 0 or 1 participant): {skipped_emails}")

        # Quick counts
        people_count = db.execute_query("SELECT COUNT(*) AS c FROM people;", fetch=True)[0]["c"]
        rel_count = db.execute_query("SELECT COUNT(*) AS c FROM relationships;", fetch=True)[0]["c"]
        print(f"  People: {people_count}")
        print(f"  Relationships: {rel_count}")

    finally:
        db.close()


if __name__ == "__main__":
    build_from_demo_emails()

