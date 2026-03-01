# API Reference - Gmail APIs System

## FastAPI Server (api_server.py)

**Base URL**: `http://localhost:8000`
**Docs**: `http://localhost:8000/docs` (Swagger UI)

### Pydantic Models

```python
class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

class EmailProcessingRequest(BaseModel):
    user_email: EmailStr
    emails: List[Dict[str, Any]]

class EmailProcessingResponse(BaseModel):
    success: bool
    message: str
    processing_stats: Dict[str, Any]
    user_id: Optional[int] = None

class RelationshipResponse(BaseModel):
    person_id: int
    person_name: str
    person_email: str
    related_person_id: int
    related_person_name: str
    related_person_email: str
    related_company: Optional[str]
    interaction_count: int
    last_interaction_date: date
    recent_subjects: str

class ExpertiseResponse(BaseModel):
    person_id: int
    expertise_name: str
    confidence_score: float
    source_email_id: Optional[str]

class InteractionResponse(BaseModel):
    id: int
    subject: str
    interaction_date: date
    summary: str
    interaction_type: str
    participant_count: int

class ProcessingStatsResponse(BaseModel):
    total_emails: int
    processed_emails: int
    filtered_emails: int
    unique_threads: int
```

### Endpoints

#### POST /users
Create a new user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response**: `UserResponse`

#### GET /users/{user_email}
Get user by email.

**Parameters**: `user_email` (path parameter)

**Response**: `UserResponse`

#### POST /process-emails
Process emails and extract relationships (runs in background).

**Request Body**:
```json
{
  "user_email": "user@example.com",
  "emails": [
    {
      "id": "email_id",
      "threadId": "thread_id",
      "From": "sender@example.com",
      "To": "recipient@example.com",
      "Subject": "Subject",
      "Date": "2024-01-01 12:00:00",
      "body": "Email content"
    }
  ]
}
```

**Response**: `EmailProcessingResponse`

#### POST /upload-emails
Upload emails from a JSON file.

**Form Data**:
- `file`: JSON file with email data
- `user_email`: User email (query parameter)

**Response**: `EmailProcessingResponse`

#### GET /users/{user_id}/relationships
Get relationships for a user.

**Parameters**:
- `user_id` (path): User ID
- `limit` (query, optional): Max results (default: 100)

**Response**: `List[RelationshipResponse]`

#### GET /users/{user_id}/expertise
Get expertise for all people associated with a user.

**Parameters**: `user_id` (path)

**Response**: `List[ExpertiseResponse]`

#### GET /users/{user_id}/interactions
Get interactions for a user within a date range.

**Parameters**:
- `user_id` (path): User ID
- `start_date` (query, optional): Start date (YYYY-MM-DD)
- `end_date` (query, optional): End date (YYYY-MM-DD)
- `limit` (query, optional): Max results (default: 100)

**Response**: `List[InteractionResponse]`

#### GET /users/{user_id}/stats
Get processing statistics for a user.

**Parameters**: `user_id` (path)

**Response**: `ProcessingStatsResponse`

#### GET /health
Health check endpoint.

**Response**: `{"status": "healthy", "timestamp": "datetime"}`

#### GET /
Root endpoint.

**Response**: `{"message": "...", "version": "1.0.0", "docs": "/docs"}`

---

## Flask Retool API (retool_api_simple.py)

**Base URL**: `http://localhost:8000`
**Note**: Runs on same port as FastAPI but should use different port in production

### Endpoints

#### GET /
Health check with database stats.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "stats": {
    "companies": 10,
    "people": 50,
    "interactions": 100,
    "expertise_areas": 10,
    "processed_emails": 200
  }
}
```

#### GET /companies
Get all companies.

**Response**:
```json
{
  "success": true,
  "companies": [
    {
      "id": 1,
      "name": "Company",
      "domain": "company.com",
      "description": "Description"
    }
  ]
}
```

#### GET /people
Get all people with company info.

**Response**:
```json
{
  "success": true,
  "people": [
    {
      "id": 1,
      "email": "person@example.com",
      "name": "Person",
      "company_id": 1,
      "company_name": "Company"
    }
  ]
}
```

#### GET /people/{person_id}/expertise
Get expertise for a specific person.

**Parameters**: `person_id` (path)

**Response**:
```json
{
  "success": true,
  "expertise": [
    {
      "expertise_id": 1,
      "expertise_name": "hiring",
      "description": "Recruitment expertise"
    }
  ]
}
```

#### POST /people/expertise
Add expertise to a person.

**Request Body**:
```json
{
  "person_email": "person@example.com",
  "expertise_name": "hiring",
  "description": "Recruitment expertise"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "person_id": 1,
    "expertise_id": 1
  }
}
```

#### GET /interactions
Get interactions with optional date filtering.

**Query Parameters**:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response**:
```json
{
  "success": true,
  "interactions": [
    {
      "id": 1,
      "email_id": "email_id",
      "thread_id": "thread_id",
      "subject": "Subject",
      "summary": "Summary",
      "date": "2024-01-01"
    }
  ]
}
```

#### POST /process-emails
Process emails from JSON file.

**Request Body**:
```json
{
  "json_file": "emails.json",
  "limit": 100
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "total": 100,
    "processed": 80,
    "filtered": 15,
    "errors": 5
  }
}
```

#### GET /stats
Get database statistics.

**Response**:
```json
{
  "success": true,
  "stats": {
    "companies": 10,
    "people": 50,
    "interactions": 100,
    "expertise_areas": 10,
    "processed_emails": 200
  }
}
```

---

## Error Response Format

### FastAPI
```json
{
  "detail": "Error message"
}
```

### Flask
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Starting the Servers

### FastAPI
```bash
cd E:\Projects\gmail-apis
python api_server.py
# Or with uvicorn directly:
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

### Flask
```bash
cd E:\Projects\gmail-apis
python retool_api_simple.py
```

---

## CORS Configuration

Both servers have CORS enabled for all origins. For production, update the `allow_origins` parameter in the CORS middleware configuration.

**FastAPI** (api_server.py, line 57-63):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Flask** (retool_api_simple.py, line 14):
```python
CORS(app)  # Enable CORS for Retool
```
