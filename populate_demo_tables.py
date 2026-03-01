"""
Populate simple demo tables with raw email data from last_1000_emails_full.json

New, simpler model:
- demo_threads: one row per Gmail thread (conversation)
- demo_emails: one row per raw email, minimal parsing, no AI / people / companies logic
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any

from retool_db_manager import RetoolDBManager


def parse_timestamp(internal_date: Optional[str], date_header: Optional[str]) -> Optional[datetime]:
    """Best-effort conversion of Gmail timestamps to a datetime."""
    # Prefer internalDate (ms since epoch)
    if internal_date:
        try:
            return datetime.fromtimestamp(int(internal_date) / 1000.0)
        except Exception:
            pass
    # Fallback: try parsing Date header if present
    if date_header:
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%d %b %Y %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(date_header, fmt)
            except ValueError:
                continue
    return None


def upsert_thread(db: RetoolDBManager, email: Dict[str, Any]) -> None:
    """Ensure a row exists in demo_threads for this email's thread, and update counts/dates."""
    thread_id = email.get("threadId")
    if not thread_id:
        return

    subject = email.get("Subject", "")
    sent_at = parse_timestamp(email.get("internalDate"), email.get("Date"))

    # Upsert thread row and keep basic aggregates
    db.execute_query(
        """
        INSERT INTO demo_threads (thread_id, subject, first_date, last_date, message_count)
        VALUES (%s, %s, %s, %s, 1)
        ON CONFLICT (thread_id) DO UPDATE
        SET
            subject = COALESCE(EXCLUDED.subject, demo_threads.subject),
            first_date = LEAST(COALESCE(demo_threads.first_date, EXCLUDED.first_date),
                               COALESCE(EXCLUDED.first_date, demo_threads.first_date)),
            last_date = GREATEST(COALESCE(demo_threads.last_date, EXCLUDED.last_date),
                                 COALESCE(EXCLUDED.last_date, demo_threads.last_date)),
            message_count = demo_threads.message_count + 1;
        """,
        (
            thread_id,
            subject or None,
            sent_at,
            sent_at,
        ),
        fetch=False,
    )


def insert_email(db: RetoolDBManager, email: Dict[str, Any]) -> None:
    """Insert a raw email row into demo_emails (no dedup logic beyond gmail_id)."""
    gmail_id = email.get("id")
    if not gmail_id:
        return

    sent_at = parse_timestamp(email.get("internalDate"), email.get("Date"))

    db.execute_query(
        """
        INSERT INTO demo_emails (
            gmail_id,
            thread_id,
            from_email,
            to_emails,
            cc_emails,
            bcc_emails,
            subject,
            snippet,
            body,
            sent_at,
            internal_date,
            raw_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (gmail_id) DO NOTHING;
        """,
        (
            gmail_id,
            email.get("threadId"),
            email.get("From"),
            email.get("To"),
            email.get("Cc"),
            email.get("Bcc"),
            email.get("Subject"),
            email.get("snippet"),
            email.get("body"),
            sent_at,
            int(email["internalDate"]) if email.get("internalDate") else None,
            json.dumps(email),
        ),
        fetch=False,
    )


def populate_demo_tables(json_file: str, limit: int = None):
    """Populate simple demo tables with raw email data (no AI / people / companies logic)."""
    print("=" * 60)
    print("Populating Simple Demo Tables from Email Data")
    print("=" * 60)
    
    # Load email data
    with open(json_file, "r", encoding="utf-8") as f:
        emails = json.load(f)
    
    # Apply limit if specified
    if limit:
        emails = emails[:limit]
    
    print(f"\nProcessing {len(emails)} emails...")
    
    db = RetoolDBManager()
    if not db.connect():
        print("[ERROR] Failed to connect to database")
        return
    
    try:
        stats = {
            "processed": 0,
            "threads_touched": set(),
            "errors": 0,
        }
        
        for i, email in enumerate(emails):
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{len(emails)} emails...")
            
            try:
                # 1) Ensure a thread row exists / is updated
                upsert_thread(db, email)
                if email.get("threadId"):
                    stats["threads_touched"].add(email["threadId"])
                
                # 2) Insert raw email row
                insert_email(db, email)
                stats["processed"] += 1
            except Exception as e:
                print(f"Error processing email {email.get('id')}: {e}")
                stats["errors"] += 1
        
        print("\n" + "=" * 60)
        print("Processing Complete!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Total emails attempted: {len(emails)}")
        print(f"  Emails inserted (unique gmail_id): {stats['processed']}")
        print(f"  Unique threads touched: {len(stats['threads_touched'])}")
        print(f"  Errors: {stats['errors']}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to populate demo tables: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # Default values
    json_file = "last_1000_emails_full.json"
    limit = 100  # Process first 100 emails by default
    
    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            print(f"[ERROR] Invalid limit: {sys.argv[2]}")
            sys.exit(1)
    
    populate_demo_tables(json_file, limit)
