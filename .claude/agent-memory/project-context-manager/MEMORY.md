# Gmail APIs Email Relationship Analysis - Agent Memory

**Last Updated**: 2025-02-24
**Project Location**: E:\Projects\gmail-apis
**Current Branch**: ygjyj
**Main Branch**: master

---

## Quick Project Summary

A multi-user email relationship analysis system that:
1. Fetches emails from Gmail API (OAuth authentication)
2. Filters newsletters/notifications using regex patterns
3. Extracts people, companies, expertise using LLM prompts
4. Stores relationships in SQLite/PostgreSQL with user isolation
5. Provides FastAPI and Flask APIs for data access
6. Integrates with Retool for dashboard visualization

---

## Core File Reference

| File | Purpose | Key Points |
|------|---------|------------|
| `api_server.py` | FastAPI REST API | Uses Pydantic models, background tasks, CORS |
| `retool_api_simple.py` | Flask API for Retool | Simpler, no Pydantic, direct DB queries |
| `database_manager.py` | DB operations (SQLite/Postgres) | Uses `demo_` prefixed tables for Retool |
| `email_processor.py` | Main processing pipeline | Thread grouping, LLM extraction |
| `email_filter.py` | Newsletter filtering | Regex patterns for senders/subjects/bodies |
| `llm_prompts.py` | LLM prompt templates | Structured JSON output prompts |
| `oauth_server.py` | Gmail OAuth flow | Saves token to `token_remote.json` |
| `fetch_last_1000_full.py` | Gmail API fetcher | Pagination for 1000 emails |
| `retool_db_manager.py` | Retool DB connection | Supports psycopg2, psycopg2-cffi, pg8000 |

---

## Database Schema Patterns

### Demo Tables (Retool Integration)
All demo tables use `demo_` prefix and simplified columns:

- `demo_companies`: id, name, domain, description
- `demo_people`: id, user_id, email, name, company_id
- `demo_expertise_areas`: id, name, description
- `demo_person_expertise`: person_id, expertise_id (junction)
- `demo_interactions`: id, user_id, email_id, thread_id, subject, summary, date
- `demo_interaction_participants`: interaction_id, person_id (junction)
- `demo_processed_emails`: user_id, email_id, thread_id

### Full Schema (SQLite/PostgreSQL)
Complete schema with additional columns in `database_schema.sql` and `database_schema_sqlite.sql`

---

## Environment Variables Required

```env
# Retool Database (for Flask API)
RETOOL_DB_HOST=host
RETOOL_DB_PORT=5432
RETOOL_DB_NAME=retool
RETOOL_DB_USER=user
RETOOL_DB_PASSWORD=password
RETOOL_DB_SSL=require

# Gmail OAuth (for oauth_server.py)
GMAIL_OAUTH_REDIRECT_URI=https://yourdomain.com/callback
FLASK_SECRET_KEY=your-secret-key
GMAIL_TOKEN_FILE=token_remote.json

# LLM API (optional - for extraction)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Important Code Patterns

### Database Manager Usage
```python
# Always use demo=True for Retool integration
db = DatabaseManager(db_type='sqlite', connection_params={'database': 'email_analysis.db'})
company_id = db.create_or_get_company(name, domain, description)
person_id = db.create_or_get_person(user_id, email, name, company_id)
```

### Retool DB Manager
```python
# Automatically uses demo_ tables
db = RetoolDBManager()
if db.connect():
    companies = db.get_companies()
    db.close()
```

### Email Processing
```python
processor = EmailProcessor(llm_client=None)  # None = basic extraction
result = processor.process_emails(emails, user_email="user@example.com")
# Returns: people, companies, interactions, expertise_instances
```

---

## API Endpoints Reference

### FastAPI (api_server.py)
- POST `/users` - Create user
- GET `/users/{email}` - Get user by email
- POST `/process-emails` - Process emails (JSON)
- POST `/upload-emails` - Upload JSON file
- GET `/users/{user_id}/relationships` - Get relationships
- GET `/users/{user_id}/interactions` - Get interactions with date filter
- GET `/users/{user_id}/expertise` - Get expertise
- GET `/users/{user_id}/stats` - Get stats
- GET `/health` - Health check

### Flask (retool_api_simple.py)
- GET `/` - Health check with stats
- GET `/companies` - Get all companies
- GET `/people` - Get all people with company info
- GET `/people/{person_id}/expertise` - Get person expertise
- POST `/people/expertise` - Add expertise to person
- GET `/interactions` - Get interactions (with start_date, end_date query params)
- POST `/process-emails` - Process emails from JSON file
- GET `/stats` - Get database stats

---

## Default Expertise Areas

hiring, growth, strategy, technology, marketing, finance, operations, sales, product, leadership

---

## Windows-Specific Notes

1. Use `requirements.txt` or `requirements_no_rust.txt` for installation
2. pg8000 is pure Python alternative to psycopg2 (no Rust dependency)
3. Virtual env activation: `.venv\Scripts\activate`
4. Use double quotes for file paths in bash commands

---

## Areas Ready for Expansion

1. **LLM Integration**: `_call_llm()` in email_processor.py is a stub
2. **Relationship Strength Analysis**: In llm_prompts.py but not fully utilized
3. **Company Relationships**: `extract_company_relationships()` prompt exists
4. **User Authentication**: APIs have no auth layer
5. **Batch Processing**: Could add async/queue processing
6. **Email Deduplication**: No duplicate detection across batches
7. **Sentiment Analysis**: Defined in prompts but not extracted
8. **Action Items**: Defined in interaction summary but not stored separately
9. **Thread Analysis**: Thread grouping exists but summary is basic
10. **Dashboard**: Retool setup documented but not implemented

---

## Git Workflow

- Main branch: `master`
- Current dev branch: `ygjyj`
- Recent commits show Retool integration work

---

## Key Dependencies

```
google-api-python-client>=2.100.0
google-auth-httplib2>=0.2.0
google-auth-oauthlib>=1.2.0
flask>=3.0.0
fastapi (for api_server.py)
uvicorn (for api_server.py)
psycopg2 or pg8000 (PostgreSQL)
python-dotenv
```

---

## Testing

- `test_system.py` - System validation
- `test_retool_system.py` - Retool integration tests
