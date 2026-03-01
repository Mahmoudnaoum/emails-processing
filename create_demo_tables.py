"""
Create demo tables in Retool PostgreSQL database
Creates tables with 'demo_' prefix to avoid conflicts with existing tables
"""
from retool_db_manager import RetoolDBManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_demo_tables():
    """Create simple demo tables in the database for raw emails + threads"""
    db = RetoolDBManager()
    
    if not db.connect():
        print("Failed to connect to database")
        return
    
    try:
        # Much simpler model:
        # - demo_threads: one row per Gmail thread / conversation
        # - demo_emails: one row per raw email message (minimal parsing only)
        create_statements = [
            # Threads / conversations
            """
            CREATE TABLE IF NOT EXISTS demo_threads (
                id SERIAL PRIMARY KEY,
                thread_id VARCHAR(255) UNIQUE NOT NULL,
                subject VARCHAR(500),
                first_date TIMESTAMP,
                last_date TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
            """,
            # Raw emails
            """
            CREATE TABLE IF NOT EXISTS demo_emails (
                id SERIAL PRIMARY KEY,
                gmail_id VARCHAR(255) UNIQUE NOT NULL,
                thread_id VARCHAR(255) REFERENCES demo_threads(thread_id) ON DELETE CASCADE,
                from_email VARCHAR(255),
                to_emails TEXT,
                cc_emails TEXT,
                bcc_emails TEXT,
                subject VARCHAR(500),
                snippet TEXT,
                body TEXT,
                sent_at TIMESTAMP,
                internal_date BIGINT,
                raw_json JSONB
            )
            """
        ]
        
        for i, statement in enumerate(create_statements, 1):
            print(f"Creating table {i}/{len(create_statements)}...")
            db.execute_query(statement, fetch=False)
        
        print("\n[SUCCESS] Simple demo tables created successfully!")
        print("\nDemo tables created:")
        print("  - demo_threads")
        print("  - demo_emails")
        
    except Exception as e:
        print(f"[ERROR] Failed to create demo tables: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Creating Demo Tables in Retool Database")
    print("=" * 60)
    create_demo_tables()
