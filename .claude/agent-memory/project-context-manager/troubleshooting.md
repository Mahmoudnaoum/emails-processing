# Troubleshooting Guide - Gmail APIs System

## Common Issues and Solutions

### 1. Database Connection Issues

**Symptom**: Connection refused or timeout

**RetoolDBManager (PostgreSQL)**:
```python
# Check environment variables in .env
RETOOL_DB_HOST=correct-host
RETOOL_DB_PORT=5432
RETOOL_DB_NAME=retool
RETOOL_DB_USER=retool
RETOOL_DB_PASSWORD=correct-password
RETOOL_DB_SSL=require  # Try 'disable' if SSL issues
```

**DatabaseManager (SQLite)**:
```python
# Check file path is absolute
db = DatabaseManager(
    db_type='sqlite',
    connection_params={'database': 'E:/Projects/gmail-apis/email_analysis.db'}
)
```

**Common Fixes**:
- Verify SSL mode (require vs disable)
- Check firewall rules
- Ensure database is running
- Try telnet to test connectivity: `telnet host port`

### 2. PostgreSQL Driver Installation Issues (Windows)

**Symptom**: Installation fails with build errors

**Issue**: psycopg2 requires Rust compiler on Windows

**Solutions**:
```bash
# Option 1: Use psycopg2-cffi (no Rust)
pip install psycopg2-cffi

# Option 2: Use pg8000 (pure Python)
pip install pg8000

# Option 3: Use pre-built wheel
pip install psycopg2-binary
```

**Files to update**: `requirements.txt` or use `requirements_no_rust.txt`

### 3. Gmail OAuth Issues

**Symptom**: Token refresh fails or authentication errors

**Checklist**:
1. Verify `credentials.json` exists and is valid
2. Check redirect URI matches in Google Cloud Console
3. Ensure token file path is correct
4. Check SCOPES match what's configured in GCP

**oauth_server.py Configuration**:
```python
# Must match GCP Console exactly
REDIRECT_URI = os.environ.get("GMAIL_OAUTH_REDIRECT_URI", "https://yourdomain.com/callback")

# Verify in GCP Console: APIs & Services -> Credentials -> OAuth 2.0 Client ID
# Authorized redirect URIs must include the exact REDIRECT_URI
```

**fetch_last_1000_full.py Configuration**:
```bash
# For local user
python fetch_last_1000_full.py

# For remote user (after OAuth flow)
set GMAIL_TOKEN_FILE=token_remote.json
python fetch_last_1000_full.py
```

### 4. Email Processing Errors

**Symptom**: Emails not being processed correctly

**Debug Steps**:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check email format
# Expected keys: id, threadId, From, To, Subject, Date, body
```

**Common Issues**:
- Missing `body` field - ensure using `fetch_last_1000_full.py` not metadata version
- Wrong date format - check `Date` header format
- Missing `threadId` - some emails don't have threads

**Filter Issues**:
```python
# Check if emails are being filtered
from email_filter import EmailFilter

filter = EmailFilter()
result = filter.should_filter_email(email)
print(f"Filter: {result.should_filter}, Reason: {result.reason}")
```

### 5. API Server Issues

**FastAPI (api_server.py)**:

**Symptom**: Server won't start

**Checks**:
```bash
# Check if port is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <pid> /F

# Check database initialization
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); print(db.initialize_database())"
```

**Symptom**: CORS errors in browser

**Fix**: Update CORS middleware in `api_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-retool-domain.com"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. Retool Integration Issues

**Symptom**: Retool can't connect to Flask API

**Checks**:
1. API server is running: `python retool_api_simple.py`
2. Check health endpoint: `curl http://localhost:8000/`
3. Verify Retool resource configuration
4. Check CORS is enabled

**Symptom**: Demo tables not found

**Fix**: Run `create_demo_tables.py`:
```bash
python create_demo_tables.py
```

**Verify tables exist**:
```python
from retool_db_manager import RetoolDBManager
db = RetoolDBManager()
if db.connect():
    stats = db.get_stats(demo=True)
    print(stats)
    db.close()
```

### 7. LLM Integration Issues

**Symptom**: LLM calls failing

**Checks**:
```python
# Verify API key is set
import os
print(os.environ.get('OPENAI_API_KEY'))  # Should print key
print(os.environ.get('ANTHROPIC_API_KEY'))
```

**Issue**: `email_processor.py` has stub implementation

**Fix**: Implement `_call_llm()` method:
```python
def _call_llm(self, prompt: str) -> str:
    if not self.llm_client:
        return '{"error": "No LLM client configured"}'

    try:
        response = self.llm_client.generate(prompt)
        return response
    except Exception as e:
        logger.error(f"LLM API call failed: {str(e)}")
        return '{"error": "LLM API call failed"}'
```

### 8. Import Errors

**Symptom**: Module not found

**Check virtual environment**:
```bash
# Activate venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Check installed packages
pip list

# Install missing
pip install -r requirements.txt
```

**Common missing packages**:
- `fastapi` - for api_server.py
- `uvicorn` - for FastAPI server
- `flask` - for Flask API
- `flask-cors` - for CORS support
- `python-dotenv` - for .env files
- `psycopg2` or `pg8000` - for PostgreSQL

### 9. Database Schema Mismatches

**Symptom**: Column not found errors

**Check schema**:
```bash
# SQLite
sqlite3 email_analysis.db ".schema people"

# PostgreSQL
psql -h host -U user -d database -c "\d demo_people"
```

**Common mismatches**:
- Full schema vs Demo schema columns
- `interaction_date` vs `date` column name
- `demo_` prefix missing

**Solution**: Use correct schema or update DatabaseManager methods

### 10. Memory Issues

**Symptom**: Out of memory when processing large email sets

**Solution**: Process in batches
```python
# Instead of processing all at once
batch_size = 100
for i in range(0, len(emails), batch_size):
    batch = emails[i:i+batch_size]
    processor.process_emails(batch, user_email)
```

## Debugging Tips

### Enable Logging
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Print Intermediate Results
```python
print(f"Processing email {email.get('id')}")
print(f"People extracted: {len(people)}")
print(f"Companies extracted: {len(companies)}")
```

### Test Database Connection
```python
# SQLite
python -c "import sqlite3; conn = sqlite3.connect('email_analysis.db'); print(conn.execute('SELECT COUNT(*) FROM users').fetchone())"

# PostgreSQL
python -c "import psycopg2; conn = psycopg2.connect(...); print('Connected')"
```

### Test API Endpoint
```bash
# Health check
curl http://localhost:8000/health

# With verbose output
curl -v http://localhost:8000/health

# POST request
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test"}'
```

## Log Files

### Check Application Logs
```bash
# If using file logging
tail -f app.log

# Check Windows Event Viewer (if configured)
eventvwr.msc
```

### Database Logs
- SQLite: No separate logs
- PostgreSQL: Check PostgreSQL log directory

## Getting Help

1. Check existing documentation:
   - `README.md`
   - `README_SYSTEM.md`
   - `PROJECT_CONTEXT.md`

2. Review error messages carefully

3. Test components in isolation:
   ```python
   # Test database
   from database_manager import DatabaseManager
   db = DatabaseManager()
   print(db.initialize_database())

   # Test email filter
   from email_filter import EmailFilter
   f = EmailFilter()
   print(f.should_filter_email(test_email))

   # Test API
   curl http://localhost:8000/health
   ```

4. Check git history for recent changes:
   ```bash
   git log --oneline -10
   git show HEAD:filename.py
   ```
