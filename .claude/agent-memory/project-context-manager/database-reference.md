# Database Reference - Gmail APIs System

## Schema Files

| File | Database Type | Purpose |
|------|--------------|---------|
| `E:\Projects\gmail-apis\database_schema.sql` | PostgreSQL | Full production schema |
| `E:\Projects\gmail-apis\database_schema_sqlite.sql` | SQLite | Full production schema (SQLite) |
| `E:\Projects\gmail-apis\retool_schema.sql` | PostgreSQL | Simplified schema for Retool |

## Database Manager Classes

| Class | File | Purpose |
|-------|------|---------|
| `DatabaseManager` | `database_manager.py` | Generic SQLite/PostgreSQL operations |
| `RetoolDBManager` | `retool_db_manager.py` | Retool-specific PostgreSQL operations |

## Table Reference

### Full Schema Tables

#### users
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| email | VARCHAR/TEXT | User email (unique) |
| name | VARCHAR/TEXT | User display name |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |
| updated_at | TIMESTAMP/DATETIME | Last update timestamp |

#### companies
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| name | VARCHAR/TEXT | Company name |
| domain | VARCHAR/TEXT | Domain (unique) |
| description | TEXT | Company description |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |
| updated_at | TIMESTAMP/DATETIME | Last update timestamp |

#### people
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| email | VARCHAR/TEXT | Email address |
| name | VARCHAR/TEXT | Person name |
| company_id | INTEGER | Foreign key to companies |
| role | VARCHAR/TEXT | Job role |
| is_primary_user | BOOLEAN | Is this the account owner? |
| relationship_strength | VARCHAR/TEXT | strong/moderate/weak/unknown |
| last_interaction_date | DATE | Last contact date |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |
| updated_at | TIMESTAMP/DATETIME | Last update timestamp |

#### expertise_areas
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| name | VARCHAR/TEXT | Expertise name (unique) |
| description | TEXT | Description |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |

**Default values**: hiring, growth, strategy, technology, marketing, finance, operations, sales, product, leadership

#### person_expertise
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| person_id | INTEGER | Foreign key to people |
| expertise_id | INTEGER | Foreign key to expertise_areas |
| confidence_score | DECIMAL/REAL | 0.0 to 1.0 |
| source_email_id | VARCHAR/TEXT | Reference email |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |

#### interactions
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| thread_id | VARCHAR/TEXT | Gmail thread ID |
| email_id | VARCHAR/TEXT | Gmail email ID |
| subject | TEXT | Email subject |
| interaction_date | DATE | Date of interaction |
| interaction_type | VARCHAR/TEXT | email/meeting/call/etc |
| summary | TEXT | LLM-generated summary |
| full_content | TEXT | Full email content |
| participant_count | INTEGER | Number of participants |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |
| updated_at | TIMESTAMP/DATETIME | Last update timestamp |

#### interaction_participants
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| interaction_id | INTEGER | Foreign key to interactions |
| person_id | INTEGER | Foreign key to people |
| role_in_interaction | VARCHAR/TEXT | sender/recipient/etc |
| is_expert | BOOLEAN | Did they provide expertise? |
| expertise_area_id | INTEGER | Foreign key to expertise_areas |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |

#### interaction_companies
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| interaction_id | INTEGER | Foreign key to interactions |
| company_id | INTEGER | Foreign key to companies |
| involvement_type | VARCHAR/TEXT | client/partner/etc |
| created_at | TIMESTAMP/DATETIME | Creation timestamp |

#### email_processing_status
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| email_id | VARCHAR/TEXT | Gmail email ID |
| thread_id | VARCHAR/TEXT | Gmail thread ID |
| processed | BOOLEAN | Was it processed? |
| filtered_out | BOOLEAN | Was it filtered? |
| filter_reason | VARCHAR/TEXT | Why filtered? |
| processing_date | TIMESTAMP/DATETIME | When processed |
| error_message | TEXT | Error if any |

### Demo Schema Tables (Retool)

All tables use `demo_` prefix with simplified columns:

- `demo_companies`: id, name, domain, description, created_at
- `demo_people`: id, user_id, email, name, company_id, created_at
- `demo_expertise_areas`: id, name, description
- `demo_person_expertise`: person_id, expertise_id
- `demo_interactions`: id, user_id, email_id, thread_id, subject, summary, date, created_at
- `demo_interaction_participants`: interaction_id, person_id
- `demo_processed_emails`: user_id, email_id, thread_id

## Database Manager Method Reference

### DatabaseManager Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `initialize_database()` | - | bool | Creates all tables |
| `create_user()` | email, name | int | Creates user, returns ID |
| `get_user_by_email()` | email | Dict | Gets user by email |
| `create_or_get_company()` | name, domain, description | int | Creates or gets company |
| `create_or_get_person()` | user_id, email, name, company_id, role, is_primary_user | int | Creates or gets person |
| `create_interaction()` | user_id, email_id, thread_id, subject, interaction_date, summary, full_content, interaction_type | int | Creates interaction |
| `add_interaction_participant()` | interaction_id, person_id, role_in_interaction, is_expert, expertise_area_id | bool | Adds participant |
| `add_expertise_to_person()` | person_id, expertise_id, confidence_score, source_email_id | bool | Adds expertise |
| `get_or_create_expertise_area()` | name, description | int | Gets or creates expertise |
| `mark_email_processed()` | user_id, email_id, thread_id, processed, filtered_out, filter_reason, error_message | bool | Marks email processed |
| `get_person_relationships()` | user_id, limit | List[Dict] | Gets relationships |
| `get_person_expertise()` | person_id | List[Dict] | Gets person expertise |
| `get_interactions_by_date_range()` | user_id, start_date, end_date | List[Dict] | Gets interactions |
| `get_processing_stats()` | user_id | Dict | Gets statistics |

### RetoolDBManager Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `connect()` | - | bool | Connects to database |
| `close()` | - | - | Closes connection |
| `execute_query()` | query, params, fetch | List[Dict] | Executes query |
| `get_companies()` | - | List[Dict] | Gets all companies |
| `get_people()` | - | List[Dict] | Gets all people |
| `get_person_expertise()` | person_id | List[Dict] | Gets person expertise |
| `get_interactions()` | start_date, end_date | List[Dict] | Gets interactions |
| `get_stats()` | demo | Dict | Gets statistics |
| `create_or_get_company()` | name, domain, description, demo | int | Creates or gets company |
| `create_or_get_person()` | user_id, email, name, company_id, demo | int | Creates or gets person |
| `get_or_create_expertise()` | name, description, demo | int | Gets or creates expertise |
| `add_expertise_to_person()` | person_id, expertise_id, demo | - | Adds expertise |
| `create_interaction()` | user_id, email_id, thread_id, subject, summary, date, demo | int | Creates interaction |
| `add_interaction_participant()` | interaction_id, person_id, demo | - | Adds participant |
| `mark_email_processed()` | user_id, email_id, thread_id, demo | - | Marks processed |
| `is_email_processed()` | user_id, email_id, thread_id, demo | bool | Checks if processed |

## Database Connections

### SQLite Connection
```python
db = DatabaseManager(
    db_type='sqlite',
    connection_params={'database': 'email_analysis.db'}
)
```

### PostgreSQL Connection
```python
db = DatabaseManager(
    db_type='postgresql',
    connection_params={
        'host': 'localhost',
        'port': 5432,
        'database': 'email_analysis',
        'user': 'postgres',
        'password': 'password'
    }
)
```

### Retool PostgreSQL Connection
Via environment variables in `.env`:
```env
RETOOL_DB_HOST=host
RETOOL_DB_PORT=5432
RETOOL_DB_NAME=retool
RETOOL_DB_USER=user
RETOOL_DB_PASSWORD=password
RETOOL_DB_SSL=require
```

## Important Notes

1. **Demo Mode**: Use `demo=True` parameter when calling RetoolDBManager methods to use `demo_` prefixed tables
2. **Cascading Deletes**: All foreign keys have ON DELETE CASCADE for data integrity
3. **Indexes**: Key columns are indexed for performance (user_id, email, date, etc.)
4. **Uniqueness**: User-email combinations are unique in people table
5. **Defaults**: Expertise areas are pre-populated with 10 default values
