# Architecture Documentation - Gmail APIs System

## System Architecture Overview

```
Gmail API (OAuth)
       |
       v
fetch_last_1000_full.py (fetches emails)
       |
       v
JSON file (last_1000_emails_full.json)
       |
       v
EmailProcessor (email_processor.py)
       |
       +---> EmailFilter (filters newsletters)
       |
       +---> LLMPrompts (generates extraction prompts)
       |
       +---> LLM API (optional - OpenAI/Anthropic)
       |
       v
DatabaseManager (stores results)
       |
       +---> SQLite (email_analysis.db)
       |
       +---> PostgreSQL (Retool database)
       |
       v
API Servers
       |
       +---> FastAPI (api_server.py)
       |
       +---> Flask (retool_api_simple.py)
       |
       v
Retool Dashboard (visualization)
```

## Component Relationships

### Core Processing Pipeline

```
1. Input: List of email dictionaries
2. EmailFilter.should_filter_email() -> FilterResult (should_keep, reason)
3. EmailProcessor._group_by_thread() -> Dict[thread_id, emails]
4. For each thread:
   - EmailProcessor._process_thread()
   - _extract_people_and_companies() -> LLM call
   - _extract_interaction_summary() -> LLM call
   - _identify_expertise() -> LLM call
   - _extract_participant_roles() -> LLM call
5. Merge results via _merge_thread_result()
6. Store via DatabaseManager methods
```

### Database Layer

```
DatabaseManager (abstracts SQLite/PostgreSQL)
|
+-- initialize_database() -> runs schema SQL
+-- create_user(), get_user_by_email()
+-- create_or_get_company()
+-- create_or_get_person()
+-- create_interaction()
+-- add_interaction_participant()
+-- add_expertise_to_person()
+-- get_or_create_expertise_area()
+-- mark_email_processed()
+-- Query methods: get_person_relationships(), get_interactions_by_date_range(), etc.

RetoolDBManager (specialized for Retool PostgreSQL)
|
+-- connect(), close()
+-- execute_query() (unified query executor)
+-- get_companies(), get_people(), get_interactions(), get_stats()
+-- demo=True parameter for demo_ table prefix
```

### API Layer

```
FastAPI (api_server.py)
|
+-- Pydantic models for validation
+-- Background tasks for async processing
+-- CORS middleware
+-- Auto-generated docs at /docs

Flask (retool_api_simple.py)
|
+-- Simpler, no Pydantic
+-- Direct DB queries
+-- Designed for Retool integration
```

## Data Flow Diagram

### Email Upload Flow

```
User uploads JSON
       |
       v
API receives request
       |
       v
Get or create user
       |
       v
Background task: process_emails_background()
       |
       v
EmailProcessor.process_emails()
       |
       v
Filter emails (newsletter detection)
       |
       v
Group by thread
       |
       v
For each email:
  - Extract people/companies
  - Create interaction record
  - Add participants
  - Identify expertise
  - Mark email processed
       |
       v
Return processing stats
```

### Query Flow (Retool)

```
Retool Dashboard
       |
       v
Flask API (retool_api_simple.py)
       |
       v
RetoolDBManager
       |
       v
PostgreSQL (Retool database)
       |
       v
Return JSON response
```

## Key Design Decisions

1. **Dual Schema Approach**: Full schema for production, demo_ prefix for Retool testing
2. **LLM Optional**: System works without LLM (basic extraction) or with LLM (advanced extraction)
3. **Thread-Based Processing**: Groups emails by thread_id for better context
4. **User Isolation**: All data scoped by user_id for multi-user support
5. **Filtering First**: Newsletter filtering happens before any processing
6. **Demo Table Prefix**: Allows testing without affecting production data

## Database Schema Evolution

### Full Schema vs Demo Schema

| Feature | Full Schema | Demo Schema |
|---------|-------------|-------------|
| People table | role, is_primary_user, relationship_strength, last_interaction_date | Only user_id, email, name, company_id |
| Interactions | full_content, interaction_type, participant_count | Only summary, date |
| Participants | role_in_interaction, is_expert, expertise_area_id | Only interaction_id, person_id |
| Expertise | confidence_score, source_email_id | Only person_id, expertise_id |
| Processing | processed, filtered_out, filter_reason, error_message | Only user_id, email_id, thread_id |

## Error Handling Patterns

1. **DatabaseManager**: Returns None on failure, logs errors
2. **EmailProcessor**: Skips failed emails, continues processing
3. **API Servers**: Return 500 on unexpected errors, 400 on validation errors
4. **RetoolDBManager**: Raises exceptions, caller must handle

## Performance Considerations

1. **Batching**: Process emails in batches to avoid memory issues
2. **Indexing**: Key columns indexed (user_id, email, date, etc.)
3. **Connection Pooling**: Not implemented yet - would benefit from it
4. **Caching**: People/companies cached during processing
5. **Pagination**: API endpoints support limit parameter

## Security Considerations

1. **API Keys**: Stored in .env (not in git)
2. **CORS**: Configured for all origins in dev (should restrict in prod)
3. **SQL Injection**: Uses parameterized queries
4. **User Isolation**: All queries scoped by user_id
5. **No Authentication**: APIs have no auth layer (TODO)
