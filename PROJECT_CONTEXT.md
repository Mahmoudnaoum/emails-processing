# Gmail APIs - Email Relationship Analysis System
## Complete Project Context File

**Last Updated:** 2026-02-17  
**Project Location:** e:/Projects/gmail-apis  
**Purpose:** Email relationship analysis system using LLMs to extract relationships, expertise, and interactions from Gmail emails.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Structure](#file-structure)
3. [Database Schemas](#database-schemas)
4. [API Endpoints](#api-endpoints)
5. [Key Components](#key-components)
6. [Recent Changes](#recent-changes)
7. [Configuration](#configuration)
8. [Setup Instructions](#setup-instructions)

---

## Project Overview

### What This System Does
A complete system for analyzing emails to extract relationships, expertise, and interactions using Large Language Models (LLMs). The system:
- Downloads emails from Gmail API
- Filters out newsletters/notifications
- Extracts people, companies, and expertise areas
- Stores data in database (SQLite or PostgreSQL)
- Provides insights through web API and Retool dashboard
- Supports multiple users (5+ users with data isolation)

### Core Pipeline
```
1. User uploads emails (JSON file or API)
   ↓
2. System filters out newsletters/notifications
   ↓
3. Emails are grouped by thread
   ↓
4. LLM extracts:
   - People and companies
   - Interaction summaries
   - Expertise areas
   - Participant roles
   ↓
5. Data is stored in database
   ↓
6. Results available via API
   ↓
7. Retool dashboard displays insights
```

---

## File Structure

### Core System Files
| File | Purpose | Key Classes/Functions |
|------|---------|---------------------|
| `database_manager.py` | Database operations (SQLite/PostgreSQL) | `DatabaseManager` class |
| `email_processor.py` | Main email processing pipeline | `EmailProcessor` class |
| `email_filter.py` | Newsletter/notification filtering | `EmailFilter` class |
| `llm_prompts.py` | LLM prompt templates | `LLMPromptTemplates` class |
| `api_server.py` | FastAPI REST API server | FastAPI app with endpoints |

### Retool Integration Files
| File | Purpose | Key Classes/Functions |
|------|---------|---------------------|
| `retool_db_manager.py` | Retool PostgreSQL connection | `RetoolDBManager` class |
| `retool_email_processor.py` | Email processor for Retool | `RetoolEmailProcessor` class |
| `retool_api_simple.py` | Flask API for Retool | Flask app with endpoints |
| `retool_schema.sql` | Retool database schema | SQL CREATE statements |
| `create_demo_tables.py` | Create demo tables with `demo_` prefix | `create_demo_tables()` function |
| `populate_demo_tables.py` | Populate demo tables with sample data | Demo data population |

### Gmail API Files
| File | Purpose |
|------|---------|
| `fetch_email_metadata.py` | Fetch latest 100 emails (metadata only) |
| `fetch_last_10_full.py` | Fetch last 10 emails with full content |
| `fetch_last_1000_full.py` | Fetch last 1000 emails with full content |
| `oauth_server.py` | OAuth server for Gmail authentication |

### Database Schema Files
| File | Purpose |
|------|---------|
| `database_schema.sql` | PostgreSQL schema (full) |
| `database_schema_sqlite.sql` | SQLite schema (full) |
| `retool_schema.sql` | Retool PostgreSQL schema (simplified) |

### Configuration & Requirements
| File | Purpose |
|------|---------|
| `.env` | Environment variables (database credentials, API keys) |
| `requirements.txt` | Full Python dependencies |
| `requirements_no_rust.txt` | Dependencies without Rust-based packages |
| `requirements_retool.txt` | Retool-specific dependencies |
| `requirements_retool_simple.txt` | Minimal Retool dependencies |

### Documentation Files
| File | Purpose |
|------|---------|
| `README.md` | Main project README |
| `README_RETOOL.md` | Retool integration guide |
| `README_SYSTEM.md` | Comprehensive system documentation |
| `PROJECT_SUMMARY.md` | Project summary and features |
| `RETOOL_SETUP.md` | Retool setup instructions |
| `RETOOL_SUMMARY.md` | Retool integration summary |
| `CLIENT_INSTRUCTIONS.md` | Instructions for clients |
| `INSTALLATION_NOTES.md` | Installation notes |
| `INSTALL_NO_RUST.md` | Installation without Rust |

### Test Files
| File | Purpose |
|------|---------|
| `test_system.py` | System validation tests |
| `test_retool_system.py` | Retool system tests |

### Batch Files (Windows)
| File | Purpose |
|------|---------|
| `Export my emails.bat` | Batch script to export emails |
| `Export my emails (1000).bat` | Batch script to export 1000 emails |

---

## Database Schemas

### Full Schema (PostgreSQL) - `database_schema.sql`

#### Tables:
1. **users** - Support for multiple users
   ```sql
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       email VARCHAR(255) UNIQUE NOT NULL,
       name VARCHAR(255) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```

2. **companies** - Organizations extracted from email domains
   ```sql
   CREATE TABLE companies (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       domain VARCHAR(255) UNIQUE NOT NULL,
       description TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```

3. **people** - Individuals identified from emails
   ```sql
   CREATE TABLE people (
       id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
       email VARCHAR(255) NOT NULL,
       name VARCHAR(255),
       company_id INTEGER REFERENCES companies(id),
       role VARCHAR(255),
       is_primary_user BOOLEAN DEFAULT FALSE,
       relationship_strength VARCHAR(50) DEFAULT 'unknown',
       last_interaction_date DATE,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(user_id, email)
   )
   ```

4. **expertise_areas** - Areas of expertise
   ```sql
   CREATE TABLE expertise_areas (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) UNIQUE NOT NULL,
       description TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```

5. **person_expertise** - Maps people to expertise areas
   ```sql
   CREATE TABLE person_expertise (
       id SERIAL PRIMARY KEY,
       person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
       expertise_id INTEGER REFERENCES expertise_areas(id) ON DELETE CASCADE,
       confidence_score DECIMAL(3,2) DEFAULT 0.5,
       source_email_id VARCHAR(255),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(person_id, expertise_id)
   )
   ```

6. **interactions** - Email conversations
   ```sql
   CREATE TABLE interactions (
       id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
       thread_id VARCHAR(255),
       email_id VARCHAR(255) NOT NULL,
       subject TEXT NOT NULL,
       interaction_date DATE NOT NULL,
       interaction_type VARCHAR(50) DEFAULT 'email',
       summary TEXT NOT NULL,
       full_content TEXT,
       participant_count INTEGER DEFAULT 2,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```

7. **interaction_participants** - People involved in interactions
   ```sql
   CREATE TABLE interaction_participants (
       id SERIAL PRIMARY KEY,
       interaction_id INTEGER REFERENCES interactions(id) ON DELETE CASCADE,
       person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
       role_in_interaction VARCHAR(100),
       is_expert BOOLEAN DEFAULT FALSE,
       expertise_area_id INTEGER REFERENCES expertise_areas(id),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(interaction_id, person_id)
   )
   ```

8. **interaction_companies** - Companies involved in interactions
   ```sql
   CREATE TABLE interaction_companies (
       id SERIAL PRIMARY KEY,
       interaction_id INTEGER REFERENCES interactions(id) ON DELETE CASCADE,
       company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
       involvement_type VARCHAR(100),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(interaction_id, company_id)
   )
   ```

9. **email_processing_status** - Track processed emails
   ```sql
   CREATE TABLE email_processing_status (
       id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
       email_id VARCHAR(255) NOT NULL,
       thread_id VARCHAR(255),
       processed BOOLEAN DEFAULT FALSE,
       filtered_out BOOLEAN DEFAULT FALSE,
       filter_reason VARCHAR(255),
       processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       error_message TEXT,
       UNIQUE(user_id, email_id)
   )
   ```

### Demo Schema (Retool) - `create_demo_tables.py`

Simplified tables with `demo_` prefix:

1. **demo_companies** - (id, name, domain, description)
2. **demo_people** - (id, user_id, email, name, company_id)
   - Removed: role, is_primary_user, relationship_strength, last_interaction_date
3. **demo_expertise_areas** - (id, name, description)
4. **demo_person_expertise** - (person_id, expertise_id)
   - Removed: confidence_score, source_email_id
5. **demo_interactions** - (id, user_id, email_id, thread_id, subject, summary, date)
   - Removed: full_content, interaction_type, participant_count
   - Changed: interaction_date → date
6. **demo_interaction_participants** - (interaction_id, person_id)
   - Removed: role_in_interaction, is_expert, expertise_area_id
7. **demo_processed_emails** - (user_id, email_id, thread_id)
   - Simplified from email_processing_status

---

## API Endpoints

### FastAPI Server (`api_server.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create a new user |
| GET | `/users/{email}` | Get user by email |
| POST | `/process-emails` | Process emails (JSON format) |
| POST | `/upload-emails` | Upload emails from file |
| GET | `/users/{id}/relationships` | Get relationships for a user |
| GET | `/users/{id}/interactions` | Get interactions with date filtering |
| GET | `/users/{id}/expertise` | Get expertise data |
| GET | `/users/{id}/stats` | Get processing statistics |

### Flask Retool API (`retool_api_simple.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check endpoint |
| GET | `/companies` | Get all companies |
| GET | `/people` | Get all people with company info |
| GET | `/people/{person_id}/expertise` | Get expertise for a specific person |
| POST | `/people/expertise` | Add expertise to a person |
| GET | `/interactions` | Get interactions with optional date filtering |
| POST | `/process-emails` | Process emails from JSON file |
| GET | `/stats` | Get database statistics |

---

## Key Components

### DatabaseManager (`database_manager.py`)

**Key Methods:**
- `create_user(email, name)` - Create a new user
- `get_user_by_email(email)` - Get user by email
- `create_or_get_company(name, domain, description)` - Create or get company
- `create_or_get_person(user_id, email, name, company_id, role, is_primary_user)` - Create or get person
- `create_interaction(user_id, email_id, thread_id, subject, interaction_date, summary, full_content, interaction_type)` - Create interaction
- `add_interaction_participant(interaction_id, person_id, role_in_interaction, is_expert, expertise_area_id)` - Add participant
- `add_expertise_to_person(person_id, expertise_id, confidence_score, source_email_id)` - Add expertise
- `get_or_create_expertise_area(name, description)` - Get or create expertise area
- `mark_email_processed(user_id, email_id, thread_id, processed, filtered_out, filter_reason, error_message)` - Mark email processed
- `get_person_relationships(user_id, limit)` - Get relationships
- `get_person_expertise(person_id)` - Get person expertise
- `get_interactions_by_date_range(user_id, start_date, end_date)` - Get interactions by date
- `get_processing_stats(user_id)` - Get processing statistics

**Recent Updates (2026-02-17):**
- All INSERT queries updated to use `demo_` prefixed table names
- Simplified column structures to match demo schema:
  - `demo_people`: Removed `role`, `is_primary_user` from INSERT
  - `demo_interactions`: Removed `full_content`, `interaction_type`, changed `interaction_date` to `date`
  - `demo_interaction_participants`: Removed `role_in_interaction`, `is_expert`, `expertise_area_id`
  - `demo_person_expertise`: Removed `confidence_score`, `source_email_id`
  - `demo_processed_emails`: Simplified to only `user_id`, `email_id`, `thread_id`

### EmailProcessor (`email_processor.py`)

**Key Methods:**
- `process_emails(emails, user_email)` - Process list of emails
- `_group_by_thread(emails)` - Group emails by thread ID
- `_process_thread(thread_emails, user_email)` - Process a thread
- `_extract_people_and_companies(email_content)` - Extract people/companies
- `_extract_interaction_summary(email_content)` - Extract interaction summary
- `_extract_expertise(email_content)` - Extract expertise areas

### EmailFilter (`email_filter.py`)

**Filter Patterns:**
- Newsletter patterns: `unsubscribe`, `newsletter`, `daily digest`, `weekly digest`, `marketing`, `promotion`, `sale`, `discount`, `offer`, `deal`, `subscription`
- Automated patterns: `noreply@`, `no-reply@`, `do-not-reply@`, `notification@`, `alerts@`, `mailer@`, `digest@`, `updates@`, `calendar@`, `meetings@`, `invitations@`, `team@`, `support@`, `billing@`, `account@`, `security@`, `privacy@`, `legal@`, `abuse@`, `postmaster@`, `admin@`
- Subject patterns: `[Newsletter]`, `Your statement`, `Your receipt`, `Your invoice`, `Your order`, `Your subscription`, `Your account`, `Your password`, `Your verification`, `Payment received`, `Transaction complete`, `Order shipped`, `Delivery update`, `Package tracking`, `Shipping notification`, `Appointment reminder`, `Meeting reminder`, `Calendar invitation`, `Event invitation`, `Welcome to`, `Thank you for`, `Confirm your`, `Verify your`, `Update your`

### LLMPromptTemplates (`llm_prompts.py`)

**Prompt Templates:**
- `extract_people_and_companies(email_content)` - Extract people and companies
- `extract_interaction_summary(email_content)` - Generate interaction summary
- `extract_expertise(email_content)` - Extract expertise areas
- `analyze_thread(thread_emails)` - Analyze email thread

### RetoolDBManager (`retool_db_manager.py`)

**Key Methods:**
- `connect()` - Establish database connection
- `close()` - Close database connection
- `execute_query(query, params, fetch)` - Execute query and return results
- `get_companies()` - Get all companies
- `get_people()` - Get all people
- `get_person_expertise(person_id)` - Get expertise for person
- `get_interactions(start_date, end_date)` - Get interactions
- `get_stats()` - Get database statistics
- `create_or_get_company(name, domain, description)` - Create or get company
- `create_or_get_person(email, name, company_id)` - Create or get person
- `is_email_processed(email_id)` - Check if email is processed
- `mark_email_processed(email_id)` - Mark email as processed

**Supported PostgreSQL Drivers:**
- psycopg2 (preferred)
- psycopg2-cffi (alternative)
- pg8000 (pure Python, no Rust)

### RetoolEmailProcessor (`retool_email_processor.py`)

**Key Methods:**
- `load_emails(json_file)` - Load emails from JSON file
- `extract_domain(email)` - Extract domain from email
- `extract_company_name(domain)` - Extract company name from domain
- `process_email(email)` - Process a single email
- `process_emails(json_file, limit)` - Process multiple emails
- `add_expertise(person_email, expertise_name, description)` - Add expertise to person

---

## Recent Changes

### 2026-02-17: Database Manager Updates
Updated [`database_manager.py`](database_manager.py:1) to match demo tables schema:

**Table Name Updates:**
- `companies` → `demo_companies`
- `people` → `demo_people`
- `expertise_areas` → `demo_expertise_areas`
- `person_expertise` → `demo_person_expertise`
- `interactions` → `demo_interactions`
- `interaction_participants` → `demo_interaction_participants`
- `email_processing_status` → `demo_processed_emails`

**Column Simplifications:**
1. [`create_or_get_person()`](database_manager.py:161): Removed `role` and `is_primary_user` from INSERT
2. [`create_interaction()`](database_manager.py:208): Removed `full_content` and `interaction_type`, changed `interaction_date` to `date`
3. [`add_interaction_participant()`](database_manager.py:241): Removed `role_in_interaction`, `is_expert`, `expertise_area_id`
4. [`add_expertise_to_person()`](database_manager.py:271): Removed `confidence_score` and `source_email_id`
5. [`mark_email_processed()`](database_manager.py:340): Removed `processed`, `filtered_out`, `filter_reason`, `error_message`

**Query Updates:**
- [`get_person_relationships()`](database_manager.py:370): Updated to query `demo_people` and `demo_companies` directly
- [`get_person_expertise()`](database_manager.py:404): Updated to query `demo_person_expertise` and `demo_expertise_areas`
- [`get_interactions_by_date_range()`](database_manager.py:432): Updated to query `demo_interactions` with `date` column
- [`get_processing_stats()`](database_manager.py:459): Simplified to only count total emails and unique threads

---

## Configuration

### Environment Variables (.env)

**Retool Database Connection:**
```env
RETOOL_DB_HOST=your-retool-db-host.com
RETOOL_DB_PORT=5432
RETOOL_DB_NAME=your-database-name
RETOOL_DB_USER=your-username
RETOOL_DB_PASSWORD=your-password
RETOOL_DB_SSL=require
```

**Gmail API:**
```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/callback
```

**LLM API (Optional):**
```env
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

---

## Setup Instructions

### 1. Install Dependencies

**Full Installation:**
```bash
pip install -r requirements.txt
```

**Without Rust (for Windows issues):**
```bash
pip install -r requirements_no_rust.txt
```

**Retool Integration (Minimal):**
```bash
pip install -r requirements_retool_simple.txt
```

### 2. Configure Environment

Copy example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials.

### 3. Create Database Tables

**Full Schema:**
```bash
# For PostgreSQL
psql -h localhost -U postgres -d email_analysis -f database_schema.sql

# For SQLite
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
```

**Demo Schema (Retool):**
```bash
python create_demo_tables.py
```

### 4. Fetch Emails

```bash
# Fetch 1000 emails with full content
python fetch_last_1000_full.py
```

### 5. Process Emails

**Using API:**
```bash
# Start FastAPI server
python api_server.py

# Or start Flask Retool API
python retool_api_simple.py
```

**Using Python Script:**
```python
from email_processor import EmailProcessor
from database_manager import DatabaseManager

db = DatabaseManager()
processor = EmailProcessor(llm_client=None)
result = processor.process_emails(emails, user_email="your@email.com")
```

### 6. Start Retool Dashboard

1. Connect Retool to your PostgreSQL database
2. Import the schema from `retool_schema.sql`
3. Create resources for each table
4. Build your dashboard using the API endpoints

---

## Key Features

### ✅ Email Filtering
- Automatically filters out newsletters, notifications, and automated emails
- Filters based on sender patterns, subject patterns, and body content
- Supports Gmail categories (PROMOTIONS, SOCIAL, UPDATES)

### ✅ LLM Extraction
- Extracts people and companies from email content
- Identifies areas of expertise demonstrated by each person
- Analyzes interaction summaries and key topics
- Handles email threads (grouped conversations)

### ✅ Multi-User Support
- Support for 5+ users with data isolation
- Each user's data is isolated by user_id
- User management via API

### ✅ Relationship Tracking
- Tracks who had expertise in each interaction
- Confidence scores for expertise claims
- Relationship strength assessment
- Last interaction date tracking

### ✅ Date-Based Filtering
- All interactions have timestamps
- Date range filtering in API
- Timeline view in Retool

### ✅ Multi-Person Interactions
- Tracks all people involved in each interaction
- Tracks all companies involved in each interaction
- Participant roles and expertise tracking

---

## Default Expertise Areas

The system includes these default expertise areas:
- hiring - Recruitment and talent acquisition
- growth - Business growth and scaling
- strategy - Strategic planning and business strategy
- technology - Technical expertise and software development
- marketing - Marketing and customer acquisition
- finance - Financial planning and investment
- operations - Business operations and management
- sales - Sales and business development
- product - Product development and management
- leadership - Leadership and team management

---

## Notes

### Important Files to Read First
1. [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md:1) - Complete project overview
2. [`README_RETOOL.md`](README_RETOOL.md:1) - Retool integration guide
3. [`README_SYSTEM.md`](README_SYSTEM.md:1) - Comprehensive system documentation

### Database Manager Update Notes
- The [`database_manager.py`](database_manager.py:1) file was updated on 2026-02-17 to use `demo_` prefixed tables
- This allows the same code to work with both full schema and demo schema
- The method signatures remain the same for backward compatibility
- Only the table names and column structures in INSERT queries changed

### Retool vs Full Schema
- **Full Schema**: Complete feature set with all columns and relationships
- **Demo Schema**: Simplified version for Retool integration with `demo_` prefix
- Use demo schema when working with Retool to avoid conflicts with existing tables

### LLM Integration
- The system supports OpenAI and Anthropic APIs
- LLM is optional for basic functionality
- Without LLM, the system still filters emails and extracts basic information
- With LLM, the system can extract relationships, expertise, and summaries

---

## Troubleshooting

### Common Issues

1. **PostgreSQL Driver Installation Issues (Windows)**
   - Use `requirements_no_rust.txt` to avoid Rust-based packages
   - Install `pg8000` as a pure Python alternative to `psycopg2`

2. **Database Connection Issues**
   - Check `.env` file for correct credentials
   - Verify SSL settings for Retool database (usually `require`)
   - Test connection with `python -c "from retool_db_manager import RetoolDBManager; db = RetoolDBManager(); print(db.connect())"`

3. **Email Processing Issues**
   - Check JSON file format matches expected structure
   - Verify email IDs are unique
   - Check filtering logic in `email_filter.py`

4. **API Server Issues**
   - Ensure database is initialized before starting server
   - Check CORS settings for Retool integration
   - Verify port is not already in use

---

## Contact & Support

For issues or questions:
- Check documentation files in the project root
- Review error logs for specific issues
- Test with `test_system.py` or `test_retool_system.py`

---

**End of Project Context File**
