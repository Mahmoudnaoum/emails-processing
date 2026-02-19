"""
Simplified Database Manager for Retool Integration
Connects directly to Retool's PostgreSQL database
Supports psycopg2, psycopg2-cffi, and pg8000 (pure Python, no Rust)
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import PostgreSQL driver in order of preference
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USING_DRIVER = 'psycopg2'
except ImportError:
    try:
        import psycopg2cffi as psycopg2
        from psycopg2cffi.extras import RealDictCursor
        USING_DRIVER = 'psycopg2-cffi'
    except ImportError:
        try:
            import pg8000
            USING_DRIVER = 'pg8000'
        except ImportError:
            raise ImportError("No PostgreSQL driver found. Install one of: psycopg2, psycopg2-cffi or pg8000")

from typing import Dict, List, Optional
from datetime import datetime, date


class RetoolDBManager:
    """Simplified database manager for Retool PostgreSQL connection"""

    def __init__(self):
        """Initialize database connection from environment variables"""
        self.conn_params = {
            'host': os.environ.get('RETOOL_DB_HOST', 'localhost'),
            'port': int(os.environ.get('RETOOL_DB_PORT', '5432') or 5432),
            'database': os.environ.get('RETOOL_DB_NAME', 'retool'),
            'user': os.environ.get('RETOOL_DB_USER', 'postgres'),
            'password': os.environ.get('RETOOL_DB_PASSWORD', ''),
            'sslmode': os.environ.get('RETOOL_DB_SSL', 'require')  # Default to require SSL for Retool
        }
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            if USING_DRIVER == 'pg8000':
                # pg8000 uses different parameter names
                print(f"Connecting to database with pg8000...")
                self.connection = pg8000.connect(
                    host=self.conn_params['host'],
                    port=int(self.conn_params['port']),
                    database=self.conn_params['database'],
                    user=self.conn_params['user'],
                    password=self.conn_params['password'],
                    ssl_context=True
                )
            else:
                # psycopg2 and psycopg2-cffi use same parameters
                # Create connection params dict
                print(f"Connecting to database with {USING_DRIVER}...")
                print(f"Host: {self.conn_params['host']}, Port: {self.conn_params['port']}, Database: {self.conn_params['database']}")
                print(f"SSL Mode: {self.conn_params['sslmode']}")
                
                conn_params = {
                    'host': self.conn_params['host'],
                    'port': int(self.conn_params['port']),
                    'database': self.conn_params['database'],
                    'user': self.conn_params['user'],
                    'password': self.conn_params['password'],
                    'sslmode': self.conn_params['sslmode']
                }
                
                self.connection = psycopg2.connect(**conn_params)
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.connection = None  # Clear connection on error
            return False

    def close(self):
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass  # Ignore close errors
            finally:
                self.connection = None

    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> List[Dict]:
        """Execute a query and return results"""
        if not self.connection:
            return []  # Return empty list if no connection
        
        try:
            if USING_DRIVER == 'pg8000':
                # pg8000 returns tuples, need to convert to dicts
                cursor = self.connection.cursor()
                cursor.execute(query, params or ())
                if fetch:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                self.connection.commit()
                return []
            else:
                # psycopg2 and psycopg2-cffi with RealDictCursor
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params or ())
                    if fetch:
                        return [dict(row) for row in cursor.fetchall()]
                    self.connection.commit()
                    return []
        except Exception as e:
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass  # Ignore rollback errors if connection is closed
            print(f"Error executing query: {e}")
            raise

    # Company operations
    def create_or_get_company(self, name: str, domain: str = None, description: str = None, demo: bool = False) -> int:
        """Create or get a company by domain"""
        if not self.connection:
            return None
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            # Check if company exists by domain
            if domain:
                result = self.execute_query(
                    f"SELECT id FROM {table_prefix}companies WHERE domain = %s",
                    (domain,)
                )
                if result:
                    return result[0]['id']
            
            # Create new company
            self.execute_query(
                f"INSERT INTO {table_prefix}companies (name, domain, description) VALUES (%s, %s, %s) RETURNING id",
                (name, domain, description),
                fetch=False
            )
            
            result = self.execute_query(
                f"SELECT id FROM {table_prefix}companies WHERE domain = %s",
                (domain,)
            )
            if result:
                return result[0]['id']
        except Exception as e:
            print(f"Error creating company: {e}")
            raise

    # Person operations
    def create_or_get_person(self, user_id: int, email: str, name: str = None, 
                          company_id: int = None, demo: bool = False) -> int:
        """Create or get a person by email"""
        if not self.connection:
            return None
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            # Check if person exists by email
            result = self.execute_query(
                f"SELECT id FROM {table_prefix}people WHERE email = %s",
                (email,)
            )
            if result:
                return result[0]['id']
            
            # Create new person
            self.execute_query(
                f"INSERT INTO {table_prefix}people (user_id, email, name, company_id) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, email, name, company_id),
                fetch=False
            )
            
            result = self.execute_query(
                f"SELECT id FROM {table_prefix}people WHERE email = %s",
                (email,)
            )
            if result:
                return result[0]['id']
        except Exception as e:
            print(f"Error creating person: {e}")
            raise

    # Expertise operations
    def get_or_create_expertise(self, name: str, description: str = None, demo: bool = False) -> int:
        """Get or create an expertise area"""
        if not self.connection:
            return None
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            # Check if expertise exists
            result = self.execute_query(
                f"SELECT id FROM {table_prefix}expertise_areas WHERE name = %s",
                (name,)
            )
            if result:
                return result[0]['id']
            
            # Create new expertise area
            self.execute_query(
                f"INSERT INTO {table_prefix}expertise_areas (name, description) VALUES (%s, %s) RETURNING id",
                (name, description),
                fetch=False
            )
            
            result = self.execute_query(
                f"SELECT id FROM {table_prefix}expertise_areas WHERE name = %s",
                (name,)
            )
            if result:
                return result[0]['id']
        except Exception as e:
            print(f"Error creating expertise: {e}")
            raise

    def add_expertise_to_person(self, person_id: int, expertise_id: int, demo: bool = False):
        """Add expertise to a person"""
        if not self.connection:
            return
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            self.execute_query(
                f"INSERT INTO {table_prefix}person_expertise (person_id, expertise_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (person_id, expertise_id),
                fetch=False
            )
        except Exception as e:
            print(f"Error adding expertise: {e}")
            raise

    # Interaction operations
    def create_interaction(self, user_id: int, email_id: str, thread_id: str = None, 
                       subject: str = None, summary: str = None, 
                       date: datetime = None, demo: bool = False) -> int:
        """Create an interaction"""
        if not self.connection:
            return None
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            self.execute_query(
                f"INSERT INTO {table_prefix}interactions (user_id, email_id, thread_id, subject, summary) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (user_id, email_id, thread_id, subject, summary),
                fetch=False
            )
            
            result = self.execute_query(
                f"SELECT id FROM {table_prefix}interactions WHERE email_id = %s",
                (email_id,)
            )
            if result:
                return result[0]['id']
        except Exception as e:
            print(f"Error creating interaction: {e}")
            raise

    def add_interaction_participant(self, interaction_id: int, person_id: int, demo: bool = False):
        """Add a participant to an interaction"""
        if not self.connection:
            return
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            self.execute_query(
                f"INSERT INTO {table_prefix}interaction_participants (interaction_id, person_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (interaction_id, person_id),
                fetch=False
            )
        except Exception as e:
            print(f"Error adding participant: {e}")
            raise

    # Processed email tracking
    def mark_email_processed(self, user_id: int, email_id: str, thread_id: str = None, demo: bool = False):
        """Mark an email as processed"""
        if not self.connection:
            return
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            self.execute_query(
                f"INSERT INTO {table_prefix}processed_emails (user_id, email_id, thread_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (user_id, email_id, thread_id),
                fetch=False
            )
        except Exception as e:
            print(f"Error marking email processed: {e}")
            raise

    def is_email_processed(self, user_id: int, email_id: str, thread_id: str = None, demo: bool = False) -> bool:
        """Check if an email has been processed"""
        if not self.connection:
            return False
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        try:
            result = self.execute_query(
                f"SELECT 1 FROM {table_prefix}processed_emails WHERE email_id = %s AND user_id = %s",
                (email_id, user_id)
            )
            return len(result) > 0
        except Exception as e:
            print(f"Error checking if email processed: {e}")
            raise

    # Stats
    def get_stats(self, demo: bool = False) -> Dict:
        """Get database statistics"""
        if not self.connection:
            return {
                'companies': 0,
                'people': 0,
                'interactions': 0,
                'expertise_areas': 0,
                'processed_emails': 0
            }
        
        # Use demo tables if demo mode is enabled
        table_prefix = 'demo_' if demo else ''
        
        stats = {}
        try:
            stats['companies'] = self.execute_query(f"SELECT COUNT(*) as count FROM {table_prefix}companies")[0]['count']
            stats['people'] = self.execute_query(f"SELECT COUNT(*) as count FROM {table_prefix}people")[0]['count']
            stats['interactions'] = self.execute_query(f"SELECT COUNT(*) as count FROM {table_prefix}interactions")[0]['count']
            stats['expertise_areas'] = self.execute_query(f"SELECT COUNT(*) as count FROM {table_prefix}expertise_areas")[0]['count']
            stats['processed_emails'] = self.execute_query(f"SELECT COUNT(*) as count FROM {table_prefix}processed_emails")[0]['count']
        except Exception as e:
            print(f"Error getting stats: {e}")
            # Return partial stats if some queries fail
        return stats
