"""
Database manager for handling all database operations for the email relationship analysis system
"""

import sqlite3
import psycopg2
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_type: str = 'sqlite', connection_params: Dict = None):
        """
        Initialize database manager
        
        Args:
            db_type: Type of database ('sqlite' or 'postgresql')
            connection_params: Database connection parameters
        """
        self.db_type = db_type
        self.connection_params = connection_params or {}
        
        if db_type == 'sqlite':
            self.connection_params.setdefault('database', 'email_analysis.db')
        elif db_type == 'postgresql':
            self.connection_params.setdefault('host', 'localhost')
            self.connection_params.setdefault('port', 5432)
            self.connection_params.setdefault('database', 'email_analysis')
            self.connection_params.setdefault('user', 'postgres')
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(**self.connection_params)
            conn.row_factory = sqlite3.Row
        elif self.db_type == 'postgresql':
            conn = psycopg2.connect(**self.connection_params)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_database(self) -> bool:
        """Initialize database with schema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.db_type == 'sqlite':
                    schema_file = 'database_schema_sqlite.sql'
                else:
                    schema_file = 'database_schema.sql'
                
                # Read and execute schema
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                
                # Execute entire schema at once using executescript
                cursor.executescript(schema_sql)
                
                conn.commit()
                logger.info("Database initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            return False
    
    def create_user(self, email: str, name: str) -> Optional[int]:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT INTO users (email, name) 
                        VALUES (?, ?)
                    """, (email, name))
                    user_id = cursor.lastrowid
                else:
                    cursor.execute("""
                        INSERT INTO users (email, name) 
                        VALUES (%s, %s) 
                        RETURNING id
                    """, (email, name))
                    user_id = cursor.fetchone()[0]
                
                conn.commit()
                logger.info(f"Created user {email} with ID {user_id}")
                return user_id
                
        except Exception as e:
            logger.error(f"Failed to create user {email}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.db_type == 'sqlite':
                    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                else:
                    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Failed to get user {email}: {str(e)}")
            return None
    
    def create_or_get_company(self, name: str, domain: str, description: str = None) -> int:
        """Create or get a company"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Try to get existing company
                if self.db_type == 'sqlite':
                    cursor.execute("SELECT id FROM demo_companies WHERE domain = ?", (domain,))
                else:
                    cursor.execute("SELECT id FROM demo_companies WHERE domain = %s", (domain,))
                
                row = cursor.fetchone()
                if row:
                    return row[0]
                
                # Create new company
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT INTO demo_companies (name, domain, description)
                        VALUES (?, ?, ?)
                    """, (name, domain, description))
                    company_id = cursor.lastrowid
                else:
                    cursor.execute("""
                        INSERT INTO demo_companies (name, domain, description)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (name, domain, description))
                    company_id = cursor.fetchone()[0]
                
                conn.commit()
                logger.info(f"Created company {name} with ID {company_id}")
                return company_id
                
        except Exception as e:
            logger.error(f"Failed to create/get company {name}: {str(e)}")
            return None
    
    def create_or_get_person(self, user_id: int, email: str, name: str = None,
                           company_id: int = None, role: str = None,
                           is_primary_user: bool = False) -> int:
        """Create or get a person"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Try to get existing person
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        SELECT id FROM demo_people
                        WHERE user_id = ? AND email = ?
                    """, (user_id, email))
                else:
                    cursor.execute("""
                        SELECT id FROM demo_people
                        WHERE user_id = %s AND email = %s
                    """, (user_id, email))
                
                row = cursor.fetchone()
                if row:
                    return row[0]
                
                # Create new person (simplified: only user_id, email, name, company_id)
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT INTO demo_people (user_id, email, name, company_id)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, email, name, company_id))
                    person_id = cursor.lastrowid
                else:
                    cursor.execute("""
                        INSERT INTO demo_people (user_id, email, name, company_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (user_id, email, name, company_id))
                    person_id = cursor.fetchone()[0]
                
                conn.commit()
                logger.info(f"Created person {email} with ID {person_id}")
                return person_id
                
        except Exception as e:
            logger.error(f"Failed to create/get person {email}: {str(e)}")
            return None
    
    def create_interaction(self, user_id: int, email_id: str, thread_id: str,
                          subject: str, interaction_date: date, summary: str,
                          full_content: str = None, interaction_type: str = 'email') -> int:
        """Create an interaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Simplified: only user_id, email_id, thread_id, subject, summary, date
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT INTO demo_interactions
                        (user_id, email_id, thread_id, subject, summary, date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, email_id, thread_id, subject, summary, interaction_date))
                    interaction_id = cursor.lastrowid
                else:
                    cursor.execute("""
                        INSERT INTO demo_interactions
                        (user_id, email_id, thread_id, subject, summary, date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (user_id, email_id, thread_id, subject, summary, interaction_date))
                    interaction_id = cursor.fetchone()[0]
                
                conn.commit()
                logger.info(f"Created interaction {email_id} with ID {interaction_id}")
                return interaction_id
                
        except Exception as e:
            logger.error(f"Failed to create interaction {email_id}: {str(e)}")
            return None
    
    def add_interaction_participant(self, interaction_id: int, person_id: int,
                                  role_in_interaction: str, is_expert: bool = False,
                                  expertise_area_id: int = None) -> bool:
        """Add a participant to an interaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Simplified: only interaction_id and person_id
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT OR REPLACE INTO demo_interaction_participants
                        (interaction_id, person_id)
                        VALUES (?, ?)
                    """, (interaction_id, person_id))
                else:
                    cursor.execute("""
                        INSERT INTO demo_interaction_participants
                        (interaction_id, person_id)
                        VALUES (%s, %s)
                        ON CONFLICT (interaction_id, person_id) DO NOTHING
                    """, (interaction_id, person_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to add interaction participant: {str(e)}")
            return False
    
    def add_expertise_to_person(self, person_id: int, expertise_id: int,
                               confidence_score: float = 0.5,
                               source_email_id: str = None) -> bool:
        """Add expertise to a person"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Simplified: only person_id and expertise_id
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT OR REPLACE INTO demo_person_expertise
                        (person_id, expertise_id)
                        VALUES (?, ?)
                    """, (person_id, expertise_id))
                else:
                    cursor.execute("""
                        INSERT INTO demo_person_expertise
                        (person_id, expertise_id)
                        VALUES (%s, %s)
                        ON CONFLICT (person_id, expertise_id) DO NOTHING
                    """, (person_id, expertise_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to add expertise to person: {str(e)}")
            return False
    
    def get_or_create_expertise_area(self, name: str, description: str = None) -> int:
        """Get or create an expertise area"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Try to get existing expertise area
                if self.db_type == 'sqlite':
                    cursor.execute("SELECT id FROM demo_expertise_areas WHERE name = ?", (name,))
                else:
                    cursor.execute("SELECT id FROM demo_expertise_areas WHERE name = %s", (name,))
                
                row = cursor.fetchone()
                if row:
                    return row[0]
                
                # Create new expertise area
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT INTO demo_expertise_areas (name, description)
                        VALUES (?, ?)
                    """, (name, description))
                    expertise_id = cursor.lastrowid
                else:
                    cursor.execute("""
                        INSERT INTO demo_expertise_areas (name, description)
                        VALUES (%s, %s)
                        RETURNING id
                    """, (name, description))
                    expertise_id = cursor.fetchone()[0]
                
                conn.commit()
                logger.info(f"Created expertise area {name} with ID {expertise_id}")
                return expertise_id
                
        except Exception as e:
            logger.error(f"Failed to get/create expertise area {name}: {str(e)}")
            return None
    
    def mark_email_processed(self, user_id: int, email_id: str, thread_id: str = None,
                           processed: bool = True, filtered_out: bool = False,
                           filter_reason: str = None, error_message: str = None) -> bool:
        """Mark an email as processed"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Simplified: only user_id, email_id, thread_id
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        INSERT OR REPLACE INTO demo_processed_emails
                        (user_id, email_id, thread_id)
                        VALUES (?, ?, ?)
                    """, (user_id, email_id, thread_id))
                else:
                    cursor.execute("""
                        INSERT INTO demo_processed_emails
                        (user_id, email_id, thread_id)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, email_id) DO NOTHING
                    """, (user_id, email_id, thread_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark email processed {email_id}: {str(e)}")
            return False
    
    def get_person_relationships(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get relationships for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Note: person_relationships view/table doesn't exist in demo schema
                # This method needs to be updated based on actual demo schema requirements
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        SELECT p.*, c.name as company_name
                        FROM demo_people p
                        LEFT JOIN demo_companies c ON p.company_id = c.id
                        WHERE p.user_id = ?
                        ORDER BY p.id DESC
                        LIMIT ?
                    """, (user_id, limit))
                else:
                    cursor.execute("""
                        SELECT p.*, c.name as company_name
                        FROM demo_people p
                        LEFT JOIN demo_companies c ON p.company_id = c.id
                        WHERE p.user_id = %s
                        ORDER BY p.id DESC
                        LIMIT %s
                    """, (user_id, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get person relationships: {str(e)}")
            return []
    
    def get_person_expertise(self, person_id: int) -> List[Dict]:
        """Get expertise for a person"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        SELECT pe.*, ea.name as expertise_name, ea.description
                        FROM demo_person_expertise pe
                        JOIN demo_expertise_areas ea ON pe.expertise_id = ea.id
                        WHERE pe.person_id = ?
                    """, (person_id,))
                else:
                    cursor.execute("""
                        SELECT pe.*, ea.name as expertise_name, ea.description
                        FROM demo_person_expertise pe
                        JOIN demo_expertise_areas ea ON pe.expertise_id = ea.id
                        WHERE pe.person_id = %s
                    """, (person_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get person expertise: {str(e)}")
            return []
    
    def get_interactions_by_date_range(self, user_id: int, start_date: date,
                                     end_date: date) -> List[Dict]:
        """Get interactions within a date range"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        SELECT * FROM demo_interactions
                        WHERE user_id = ? AND date BETWEEN ? AND ?
                        ORDER BY date DESC
                    """, (user_id, start_date, end_date))
                else:
                    cursor.execute("""
                        SELECT * FROM demo_interactions
                        WHERE user_id = %s AND date BETWEEN %s AND %s
                        ORDER BY date DESC
                    """, (user_id, start_date, end_date))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get interactions by date range: {str(e)}")
            return []
    
    def get_processing_stats(self, user_id: int) -> Dict:
        """Get processing statistics for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Simplified: demo_processed_emails only has user_id, email_id, thread_id
                if self.db_type == 'sqlite':
                    cursor.execute("""
                        SELECT
                            COUNT(*) as total_emails,
                            COUNT(DISTINCT thread_id) as unique_threads
                        FROM demo_processed_emails
                        WHERE user_id = ?
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT
                            COUNT(*) as total_emails,
                            COUNT(DISTINCT thread_id) as unique_threads
                        FROM demo_processed_emails
                        WHERE user_id = %s
                    """, (user_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else {}
                
        except Exception as e:
            logger.error(f"Failed to get processing stats: {str(e)}")
            return {}

# Example usage
if __name__ == "__main__":
    # Initialize database manager
    db_manager = DatabaseManager(db_type='sqlite')
    
    # Initialize database
    if db_manager.initialize_database():
        print("Database initialized successfully")
        
        # Create a test user
        user_id = db_manager.create_user('test@example.com', 'Test User')
        if user_id:
            print(f"Created user with ID: {user_id}")
            
            # Get processing stats
            stats = db_manager.get_processing_stats(user_id)
            print(f"Processing stats: {stats}")
    else:
        print("Failed to initialize database")