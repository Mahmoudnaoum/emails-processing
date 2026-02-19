# Email Relationship Analysis System - Retool Integration

A simplified email processing system that connects directly to your Retool PostgreSQL database to extract and store relationships from your Gmail emails.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_no_rust.txt
```

### 2. Configure Database Connection

Copy the example environment file and fill in your Retool database credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Retool database details:

```env
RETOOL_DB_HOST=your-retool-db-host.com
RETOOL_DB_PORT=5432
RETOOL_DB_NAME=your-database-name
RETOOL_DB_USER=your-username
RETOOL_DB_PASSWORD=your-password
```

### 3. Create Database Tables

Run the schema SQL in your Retool database:

```bash
# Option 1: Copy and paste the SQL into Retool's SQL editor
cat retool_schema.sql

# Option 2: Use psql if you have direct access
psql -h your-host -U your-user -d your-database -f retool_schema.sql
```

### 4. Test the System

```bash
python setup_retool.py
```

### 5. Start the API Server

```bash
python retool_api_simple.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /
```
Returns system health and database statistics.

### Companies
```
GET /companies
```
Get all companies.

### People
```
GET /people
```
Get all people with company information.

```
GET /people/{person_id}/expertise
```
Get expertise areas for a specific person.

```
POST /people/expertise
```
Add expertise to a person.

**Request Body:**
```json
{
  "person_email": "john@example.com",
  "expertise_name": "Python Development",
  "description": "Expert in Python and Django"
}
```

### Interactions
```
GET /interactions
```
Get all interactions.

**Query Parameters:**
- `start_date` (optional): Filter interactions from this date (YYYY-MM-DD)
- `end_date` (optional): Filter interactions until this date (YYYY-MM-DD)

Example: `GET /interactions?start_date=2024-01-01&end_date=2024-12-31`

### Processing
```
POST /process-emails
```
Process emails from a JSON file.

**Request Body:**
```json
{
  "json_file": "last_1000_emails_full.json",
  "limit": 100
}
```

### Statistics
```
GET /stats
```
Get database statistics.

## Database Schema

The system uses 6 main tables:

### companies
- `id` - Primary key
- `name` - Company name
- `domain` - Email domain (e.g., example.com)
- `description` - Optional description

### people
- `id` - Primary key
- `email` - Email address (unique)
- `name` - Person's name
- `company_id` - Foreign key to companies

### expertise_areas
- `id` - Primary key
- `name` - Expertise area name (unique)
- `description` - Optional description

### person_expertise
- `person_id` - Foreign key to people
- `expertise_id` - Foreign key to expertise_areas

### interactions
- `id` - Primary key
- `email_id` - Gmail email ID (unique)
- `thread_id` - Gmail thread ID
- `subject` - Email subject
- `summary` - Email summary
- `date` - Email date

### interaction_participants
- `interaction_id` - Foreign key to interactions
- `person_id` - Foreign key to people

### processed_emails
- `email_id` - Primary key
- `processed_at` - Timestamp

## Processing Emails

### Using the API

```bash
curl -X POST http://localhost:8000/process-emails \
  -H "Content-Type: application/json" \
  -d '{
    "json_file": "last_1000_emails_full.json",
    "limit": 100
  }'
```

### Using Python Script

```python
from retool_email_processor import RetoolEmailProcessor

processor = RetoolEmailProcessor()
result = processor.process_emails("last_1000_emails_full.json", limit=100)
print(result)
```

## Email Filtering

The system automatically filters out:
- Newsletters
- Notifications
- Automated messages
- Promotional emails

Only personal and business communications are processed.

## Retool Integration

### Connecting to the API

In Retool, create a new REST API resource:

1. **Base URL**: `http://localhost:8000` (or your deployed URL)
2. **Authentication**: None (or add API key if needed)

### Example Retool Queries

**People Table:**
```
GET {{ resource.url }}/people
```

**Interactions:**
```
GET {{ resource.url }}/interactions?start_date={{ dateInput }}&end_date={{ dateInput2 }}
```

**Add Expertise:**
```
POST {{ resource.url }}/people/expertise
Body:
{
  "person_email": "{{ email }}",
  "expertise_name": "{{ expertise }}"
}
```

### Example Retool Dashboard

1. **People Table**
   - Query: `GET /people`
   - Display: Name, Email, Company

2. **Interactions Timeline**
   - Query: `GET /interactions`
   - Display: Date, Subject, Participants

3. **Expertise Management**
   - Query: `POST /people/expertise`
   - Input: Email, Expertise Name

4. **Statistics**
   - Query: `GET /stats`
   - Display: Total companies, people, interactions

## File Structure

```
.
├── retool_schema.sql           # Database schema
├── retool_db_manager.py        # Database manager
├── retool_email_processor.py   # Email processor
├── retool_api_simple.py       # Flask API server (no pydantic required)
├── email_filter.py            # Email filtering logic
├── llm_prompts.py             # LLM prompt templates
├── test_retool_system.py      # Test script
├── requirements_no_rust.txt    # Python dependencies (no Rust)
├── .env.example               # Environment variables template
└── README_RETOOL.md           # This file
```

## Troubleshooting

### Database Connection Failed

1. Check your `.env` file has correct credentials
2. Ensure your Retool database allows external connections
3. Verify the database host and port are correct

### No Emails Processed

1. Check if your email JSON file exists
2. Verify the JSON format matches Gmail API format
3. Check that emails are not all filtered as newsletters

### API Not Responding

1. Ensure the API server is running: `python retool_api_simple.py`
2. Check the port 8000 is not in use
3. Verify CORS settings if calling from Retool

## Key Features

- **No Rust Required**: Uses pure Python libraries (pg8000, Flask)
- **Direct Database Connection**: Connects directly to Retool PostgreSQL
- **Email Filtering**: Automatically filters newsletters and notifications
- **Relationship Extraction**: Extracts people, companies, and interactions
- **Expertise Tracking**: Track who provided what expertise
- **Date Filtering**: Filter interactions by date range
- **Multi-Person Support**: Track all participants in each interaction
- **Company Associations**: Extract companies from email domains

## License

MIT
