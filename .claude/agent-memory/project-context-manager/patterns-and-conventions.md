# Patterns and Conventions - Gmail APIs System

## Code Style Patterns

### File Naming
- Snake case for Python files: `email_processor.py`, `database_manager.py`
- Descriptive names: `retool_api_simple.py` vs `api.py`
- Test files prefixed: `test_*.py`

### Class Naming
- PascalCase for classes: `EmailProcessor`, `DatabaseManager`, `LLMPromptTemplates`
- Descriptive suffixes: `*Manager`, `*Processor`, `*Filter`

### Method Naming
- Snake case for methods: `create_or_get_person()`, `get_user_by_email()`
- Verb-first for actions: `create_*`, `get_*`, `add_*`, `mark_*`
- Boolean queries: `is_*`, `should_*`: `E:\Projects\gmail-apis\.env`
- Gmail OAuth: `GMAIL_OAUTH_REDIRECT_URI`, `FLASK_SECRET_KEY`
- LLM API: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`

### Secrets (never committed)
- `credentials.json` - Gmail OAuth credentials
- `token.json` - Gmail OAuth token
- `token_remote.json` - Remote user OAuth token
- `.env` - Environment variables

### Documentation
- `README*.md` - User-facing documentation
- `PROJECT_*.md` - Project documentation
- `*_SETUP.md` - Setup instructions
- `*_NOTES.md` - Developer notes

## Database Patterns

### Table Naming
- Plural snake case: `users`, `people`, `companies`, `interactions`
- Junction tables: `person_expertise`, `interaction_participants`
- Status tables: `email_processing_status`, `processed_emails`

### Column Naming
- Snake case: `user_id`, `company_id`, `interaction_date`
- Foreign keys: `{table}_id` (e.g., `user_id`, `company_id`)
- Boolean prefixes: `is_primary_user`, `is_expert`
- Timestamps: `created_at`, `updated_at`

### Demo Table Convention
- Prefix with `demo_`: `demo_people`, `demo_companies`
- Used for Retool integration
- Simplified columns compared to full schema

## API Patterns

### FastAPI Endpoints
- RESTful naming: `/users`, `/process-emails`
- Path parameters: `/users/{user_id}`
- Query parameters: `?limit=100&start_date=2024-01-01`
- Resource hierarchy: `/users/{id}/relationships`, `/users/{id}/interactions`

### Flask Endpoints
- Simple RESTful: `/companies`, `/people`, `/interactions`
- Nested resources: `/people/{id}/expertise`
- Action endpoints: `/process-emails`

### Response Format
**FastAPI** - Pydantic models:
```python
class Response(BaseModel):
    field: type
```

**Flask** - Manual dicts:
```python
return jsonify({"success": True, "data": result})
```

## Error Handling Patterns

### Database Manager
```python
try:
    # Database operation
    return result
except Exception as e:
    logger.error(f"Error: {e}")
    return None  # or False
```

### API Endpoints
```python
try:
    # Process request
    return result
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail="Error")
```

## Common Patterns

### Context Manager Pattern
```python
@contextmanager
def get_connection(self):
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
```

### Factory Pattern
```python
def create_or_get_*(self, ...):
    # Try to get existing
    result = self.get_*(...)
    if result:
        return result
    # Create new
    return self.create_*(...)
```

### Background Task Pattern
```python
@app.post("/process")
def process(request):
    background_tasks.add_task(process_background, ...)
    return {"status": "started"}
```

## Import Conventions

### Standard Library
```python
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional
```

### Third Party
```python
from fastapi import FastAPI, HTTPException
from flask import Flask, jsonify, request
import sqlite3
import psycopg2
```

### Local Imports
```python
from email_processor import EmailProcessor
from database_manager import DatabaseManager
from llm_prompts import LLMPromptTemplates
```

## Logging Conventions

```python
# Configure at module level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usage
logger.info(f"Processing {len(emails)} emails")
logger.error(f"Failed to process: {error}")
```

## Type Hint Conventions

```python
from typing import Dict, List, Optional, Any, Tuple

def process_emails(
    emails: List[Dict],
    user_email: str
) -> Dict[str, Any]:
    ...

def get_user(
    email: str
) -> Optional[Dict]:
    ...
```

## Database Query Patterns

### Parameterized Queries
```python
# SQLite
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))

# PostgreSQL
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

### Connection Pattern
```python
with self.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(...)
    conn.commit()
```

## Return Value Conventions

### Success Indicators
- `True`/`False` for operations
- `int` ID for created records
- `Dict` for fetched records
- `List[Dict]` for multiple records
- `None` for failure/not found

### Error Returns
- `None` for "not found" in get operations
- `False` for operation failure
- Raise exception for critical errors

## Configuration Pattern

### Environment Loading
```python
from dotenv import load_dotenv
import os

load_dotenv()

value = os.environ.get('KEY', 'default_value')
```

### Connection Params Dict
```python
self.connection_params = {
    'host': os.environ.get('HOST', 'localhost'),
    'port': int(os.environ.get('PORT', '5432')),
    'database': os.environ.get('DATABASE', 'db'),
    ...
}
```

## Testing Patterns

### Test File Naming
- `test_*.py` for test modules
- `test_system.py` for integration tests
- `test_retool_system.py` for Retool-specific tests

## Comment Conventions

### Docstrings
```python
def method(self, param: type) -> return_type:
    """
    Brief description.

    Args:
        param: Description

    Returns:
        Description of return value
    """
```

### Inline Comments
- Use `#` for single-line comments
- Place above the code being commented
- Explain "why" not "what"

## Git Conventions

### Branch Names
- Feature branches: descriptive names
- Current dev: `ygjyj`
- Main: `master`

### Commit Messages
- Conventional commits: "Add feature", "Fix bug"
- Recent pattern: "Add Retool integration", "Remove sensitive credentials"
