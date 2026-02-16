# Email Relationship Analysis System

A comprehensive system for analyzing emails to extract relationships, expertise, and interactions using LLMs and database storage. Designed to support multiple users with a Retool frontend interface.

## System Overview

This system processes emails to:
- Filter out newsletters and notifications
- Extract people and companies mentioned
- Identify areas of expertise
- Analyze relationship strength
- Store interactions in a database
- Provide insights through API endpoints and Retool dashboard

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gmail API    │───▶│  Email Processor │───▶│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   LLM Service    │    │   API Server    │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Retool App    │
                                               └─────────────────┘
```

## Components

### 1. Email Processing Pipeline

**Files:**
- `email_filter.py` - Filters newsletters and notifications
- `llm_prompts.py` - LLM prompt templates for extraction
- `email_processor.py` - Main processing pipeline
- `fetch_last_1000_full.py` - Gmail API integration

**Features:**
- Smart filtering of automated content
- Thread-based email processing
- Multi-language support
- LLM-powered relationship extraction

### 2. Database Schema

**Files:**
- `database_schema.sql` - PostgreSQL schema
- `database_schema_sqlite.sql` - SQLite schema
- `database_manager.py` - Database operations

**Tables:**
- `users` - Multi-user support
- `people` - Individuals identified
- `companies` - Organizations extracted
- `interactions` - Email conversations
- `expertise_areas` - Areas of expertise
- `person_expertise` - Expertise mappings
- `interaction_participants` - Who was involved

### 3. API Server

**File:** `api_server.py`

**Endpoints:**
- `POST /users` - Create user
- `POST /process-emails` - Process emails
- `GET /users/{id}/relationships` - Get relationships
- `GET /users/{id}/interactions` - Get interactions
- `GET /users/{id}/expertise` - Get expertise
- `POST /upload-emails` - Upload JSON emails

### 4. Retool Integration

**Features:**
- User management dashboard
- Email upload interface
- Relationship visualization
- Expertise tracking
- Interaction timeline
- Multi-user support

## Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Mahmoudnaoum/emails-processing.git
cd emails-processing

# Install dependencies
pip install -r requirements_new.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 2. Database Setup

**Option A: SQLite (Development)**
```bash
# Database will be created automatically
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
```

**Option B: PostgreSQL (Production)**
```bash
# Create database
createdb email_analysis

# Run schema
psql -d email_analysis -f database_schema.sql
```

### 3. Gmail API Setup

1. Follow `CLIENT_INSTRUCTIONS.md` for OAuth setup
2. Create `credentials.json` with your Gmail API credentials
3. Run `fetch_last_1000_full.py` to export emails

### 4. Start API Server

```bash
python api_server.py
```

Server will be available at `http://localhost:8000`

### 5. Retool Setup

1. Create new Retool application
2. Add API resource pointing to `http://localhost:8000`
3. Import the Retool JSON configuration (when provided)
4. Configure authentication if needed

## Usage

### Processing Emails

**Via API:**
```python
import requests

emails = [...]  # Your email data
response = requests.post('http://localhost:8000/process-emails', json={
    'user_email': 'user@example.com',
    'emails': emails
})
```

**Via File Upload:**
```bash
curl -X POST "http://localhost:8000/upload-emails" \
  -H "user-email: user@example.com" \
  -F "file=@emails.json"
```

### Querying Data

**Get Relationships:**
```bash
curl "http://localhost:8000/users/1/relationships?limit=50"
```

**Get Interactions:**
```bash
curl "http://localhost:8000/users/1/interactions?start_date=2024-01-01&end_date=2024-12-31"
```

**Get Expertise:**
```bash
curl "http://localhost:8000/users/1/expertise"
```

## Data Models

### Email Input Format
```json
{
  "id": "email_id",
  "threadId": "thread_id",
  "From": "sender@example.com",
  "To": "recipient@example.com",
  "Subject": "Email subject",
  "Date": "2024-01-01 12:00:00",
  "body": "Email content",
  "labelIds": ["INBOX", "IMPORTANT"]
}
```

### Relationship Output
```json
{
  "person_id": 1,
  "person_name": "John Doe",
  "person_email": "john@example.com",
  "related_person_id": 2,
  "related_person_name": "Jane Smith",
  "related_person_email": "jane@example.com",
  "related_company": "Acme Corp",
  "interaction_count": 15,
  "last_interaction_date": "2024-01-15",
  "recent_subjects": "Project Update; Meeting Schedule"
}
```

### Expertise Output
```json
{
  "person_id": 1,
  "expertise_name": "hiring",
  "confidence_score": 0.85,
  "source_email_id": "email_123"
}
```

## LLM Integration

The system supports multiple LLM providers:

### OpenAI Integration
```python
import openai

class OpenAIClient:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
```

### Anthropic Integration
```python
import anthropic

class AnthropicClient:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(self, prompt):
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

## Multi-User Support

The system is designed to support multiple users:

1. **User Isolation**: Each user's data is completely isolated
2. **Scalable Architecture**: Can handle 5+ users simultaneously
3. **Resource Management**: Efficient database queries and caching
4. **Permission System**: Users can only access their own data

## Performance Considerations

### Email Processing
- Batch processing for large email sets
- Background task processing
- Progress tracking and status updates
- Error handling and retry logic

### Database Optimization
- Indexed queries for fast lookups
- Connection pooling
- Query optimization for relationship graphs
- Caching frequently accessed data

### API Performance
- Async request handling
- Rate limiting
- Response pagination
- Efficient JSON serialization

## Security Features

1. **Data Encryption**: Sensitive data encrypted at rest
2. **API Authentication**: Token-based authentication
3. **Input Validation**: Comprehensive input sanitization
4. **Rate Limiting**: Prevent abuse and ensure fair usage
5. **Audit Logging**: Track all data access and modifications

## Monitoring and Logging

### Structured Logging
```python
import structlog

logger = structlog.get_logger()
logger.info("Email processing started", user_id=user_id, email_count=len(emails))
```

### Metrics Tracking
- Processing time per email
- LLM API usage and costs
- Database query performance
- User activity patterns

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_new.txt .
RUN pip install -r requirements_new.txt

COPY . .
EXPOSE 8000

CMD ["python", "api_server.py"]
```

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@localhost/email_analysis
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
RETOOL_API_KEY=your_retool_key
LOG_LEVEL=INFO
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database URL configuration
   - Verify database is running
   - Check network connectivity

2. **LLM API Failures**
   - Verify API keys are valid
   - Check rate limits
   - Monitor API costs

3. **Email Processing Errors**
   - Check email format
   - Verify Gmail API credentials
   - Check filtering logic

4. **Performance Issues**
   - Monitor database query times
   - Check memory usage
   - Optimize batch sizes

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python api_server.py
```

## Future Enhancements

1. **Advanced Analytics**
   - Relationship strength scoring
   - Network graph visualization
   - Sentiment analysis over time

2. **Integration Features**
   - Calendar integration
   - CRM system connections
   - Slack/Teams notifications

3. **Machine Learning**
   - Custom relationship models
   - Predictive analytics
   - Anomaly detection

4. **User Experience**
   - Mobile app
   - Real-time updates
   - Advanced search capabilities

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check the application logs
4. Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.