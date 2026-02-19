"""
Simple setup script for Retool integration
Helps you get started quickly
"""
import os
import sys


def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    # Check for PostgreSQL driver
    pg_driver_installed = False
    driver_name = None
    
    try:
        __import__('psycopg2')
        print("[OK] psycopg2 (standard)")
        pg_driver_installed = True
        driver_name = "psycopg2"
    except ImportError:
        try:
            __import__('psycopg2cffi')
            print("[OK] psycopg2-cffi (pure Python)")
            pg_driver_installed = True
            driver_name = "psycopg2-cffi"
        except ImportError:
            try:
                __import__('pg8000')
                print("[OK] pg8000 (pure Python, no Rust)")
                pg_driver_installed = True
                driver_name = "pg8000"
            except ImportError:
                print("[FAIL] PostgreSQL driver NOT INSTALLED")
    
    # Check other dependencies
    required = ['flask', 'flask_cors']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[FAIL] {package} - NOT INSTALLED")
            missing.append(package)

    if not pg_driver_installed or missing:
        print(f"\n[WARNING] Missing packages detected")
        print("Install with: pip install -r requirements_no_rust.txt")
        return False

    print(f"\n[OK] All dependencies installed! Using {driver_name}")
    return True


def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...")
    if os.path.exists('.env'):
        print("[OK] .env file found")
        return True
    else:
        print("[FAIL] .env file not found")
        print("Copy .env.example to .env and fill in your database credentials")
        print("Run: cp .env.example .env")
        return False


def check_email_file():
    """Check if email JSON file exists"""
    print("\nChecking email data...")
    email_file = "last_1000_emails_full.json"
    if os.path.exists(email_file):
        print(f"[OK] {email_file} found")
        return True
    else:
        print(f"[FAIL] {email_file} not found")
        print("Place your Gmail export JSON file in the project directory")
        return False


def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from retool_db_manager import RetoolDBManager
        db = RetoolDBManager()
        if db.connect():
            print("[OK] Database connected successfully!")
            stats = db.get_stats(demo=True)  # Use demo tables
            print(f"[INFO] Current stats: {stats}")
            db.close()
            return True
        else:
            print("[FAIL] Failed to connect to database")
            print("Check your .env file for correct credentials")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def print_next_steps():
    """Print next steps"""
    print("\n" + "=" * 60)
    print("Setup Complete! Next Steps:")
    print("=" * 60)
    print("\n1. Run the test script:")
    print("   python test_retool_system.py")
    print("\n2. Start the API server:")
    print("   python retool_api_simple.py")
    print("\n3. Access the API:")
    print("   http://localhost:8000")
    print("\n4. Connect Retool:")
    print("   Create a REST API resource with base URL: http://localhost:8000")
    print("\nFor detailed instructions, see README_RETOOL.md")


def main():
    """Run setup checks"""
    print("=" * 60)
    print("Retool Email Processing System - Setup")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check environment file
    if not check_env_file():
        print("\n[WARNING] Please create .env file before continuing")
        sys.exit(1)

    # Check email file
    if not check_email_file():
        print("\n[WARNING] Please place your email JSON file before processing")
        print("You can still test the database connection though")

    # Test database connection
    if not test_database_connection():
        sys.exit(1)

    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
