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
    """Create demo tables in the database"""
    db = RetoolDBManager()
    
    if not db.connect():
        print("Failed to connect to database")
        return
    
    try:
        # Create demo tables
        create_statements = [
            # Companies table
            """
            CREATE TABLE IF NOT EXISTS demo_companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                domain VARCHAR(255) UNIQUE,
                description TEXT
            )
            """,
            
            # People table
            """
            CREATE TABLE IF NOT EXISTS demo_people (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                company_id INTEGER REFERENCES demo_companies(id) ON DELETE SET NULL
            )
            """,
            
            # Expertise areas table
            """
            CREATE TABLE IF NOT EXISTS demo_expertise_areas (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT
            )
            """,
            
            # Person-expertise relationship table
            """
            CREATE TABLE IF NOT EXISTS demo_person_expertise (
                person_id INTEGER REFERENCES demo_people(id) ON DELETE CASCADE,
                expertise_id INTEGER REFERENCES demo_expertise_areas(id) ON DELETE CASCADE,
                PRIMARY KEY (person_id, expertise_id)
            )
            """,
            
            # Interactions table
            """
            CREATE TABLE IF NOT EXISTS demo_interactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                email_id VARCHAR(255) UNIQUE NOT NULL,
                thread_id VARCHAR(255),
                subject VARCHAR(500),
                summary TEXT,
                date TIMESTAMP
            )
            """,
            
            # Interaction participants table
            """
            CREATE TABLE IF NOT EXISTS demo_interaction_participants (
                interaction_id INTEGER REFERENCES demo_interactions(id) ON DELETE CASCADE,
                person_id INTEGER REFERENCES demo_people(id) ON DELETE CASCADE,
                PRIMARY KEY (interaction_id, person_id)
            )
            """,
            
            # Processed emails table
            """
            CREATE TABLE IF NOT EXISTS demo_processed_emails (
                user_id INTEGER NOT NULL,
                email_id VARCHAR(255) NOT NULL,
                thread_id VARCHAR(255),
                PRIMARY KEY (user_id, email_id)
            )
            """
        ]
        
        # Execute each create statement
        for i, statement in enumerate(create_statements, 1):
            print(f"Creating table {i}/{len(create_statements)}...")
            db.execute_query(statement, fetch=False)
        
        print("\n[SUCCESS] All demo tables created successfully!")
        print("\nDemo tables created:")
        print("  - demo_companies")
        print("  - demo_people")
        print("  - demo_expertise_areas")
        print("  - demo_person_expertise")
        print("  - demo_interactions")
        print("  - demo_interaction_participants")
        print("  - demo_processed_emails")
        
    except Exception as e:
        print(f"[ERROR] Failed to create demo tables: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Creating Demo Tables in Retool Database")
    print("=" * 60)
    create_demo_tables()
