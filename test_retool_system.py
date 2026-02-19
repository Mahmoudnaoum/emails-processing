"""
Simple test script for Retool integration
Tests the email processing system with sample data
"""
import os
from retool_db_manager import RetoolDBManager
from retool_email_processor import RetoolEmailProcessor


def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    db = RetoolDBManager()
    if db.connect():
        print("[OK] Database connected successfully!")
        stats = db.get_stats()
        print(f"[INFO] Database stats: {stats}")
        db.close()
        return True
    else:
        print("[FAIL] Failed to connect to database")
        return False


def test_email_processing():
    """Test email processing with sample data"""
    print("\nTesting email processing...")
    processor = RetoolEmailProcessor()

    # Check if email file exists
    email_file = "last_1000_emails_full.json"
    if not os.path.exists(email_file):
        print(f"[FAIL] Email file not found: {email_file}")
        return False

    # Process first 10 emails
    print(f"Processing first 10 emails from {email_file}...")
    result = processor.process_emails(email_file, limit=10)

    print(f"\n[INFO] Processing Results:")
    print(f"   Total emails: {result['total']}")
    print(f"   Processed: {result['processed']}")
    print(f"   Filtered (newsletters): {result['filtered']}")
    print(f"   Errors: {result['errors']}")

    if result['processed'] > 0:
        print(f"\n[OK] Successfully processed {result['processed']} emails!")
        print("\nSample processed emails:")
        for detail in result['details'][:3]:
            print(f"   - {detail['subject'][:50]}... ({detail['participants']} participants)")
        return True
    else:
        print("[WARNING] No emails were processed (all filtered or errors)")
        return False


def test_retrieval():
    """Test data retrieval"""
    print("\nTesting data retrieval...")
    db = RetoolDBManager()
    if db.connect():
        try:
            # Get companies
            companies = db.get_companies()
            print(f"[OK] Found {len(companies)} companies")

            # Get people
            people = db.get_people()
            print(f"[OK] Found {len(people)} people")

            # Get interactions
            interactions = db.get_interactions()
            print(f"[OK] Found {len(interactions)} interactions")

            if interactions:
                print(f"\n[INFO] Latest interaction:")
                latest = interactions[0]
                print(f"   Subject: {latest['subject'][:50]}...")
                print(f"   Date: {latest['date']}")
                print(f"   Participants: {len(latest['participants'])}")

            return True
        finally:
            db.close()
    return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Retool Email Processing System - Test Suite")
    print("=" * 60)

    # Test 1: Database connection
    if not test_database_connection():
        print("\n[FAIL] Database connection test failed. Please check your .env file.")
        return

    # Test 2: Email processing
    if not test_email_processing():
        print("\n[WARNING] Email processing test had issues")

    # Test 3: Data retrieval
    if not test_retrieval():
        print("\n[WARNING] Data retrieval test had issues")

    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
