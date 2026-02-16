"""
FastAPI server for email relationship analysis system
Provides REST API endpoints for processing emails and managing relationships
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime, date
import os
from contextlib import asynccontextmanager

from email_processor import EmailProcessor
from database_manager import DatabaseManager
from llm_prompts import LLMPromptTemplates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for processor and database
email_processor = None
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources"""
    global email_processor, db_manager
    
    # Initialize database
    db_manager = DatabaseManager(db_type='sqlite', connection_params={'database': 'email_analysis.db'})
    if not db_manager.initialize_database():
        logger.error("Failed to initialize database")
        raise Exception("Database initialization failed")
    
    # Initialize email processor (without LLM for now)
    email_processor = EmailProcessor(llm_client=None)
    
    logger.info("Application initialized successfully")
    yield
    
    # Cleanup
    logger.info("Application shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Email Relationship Analysis API",
    description="API for processing emails and extracting relationships, expertise, and interactions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
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

# Dependency to get database manager
async def get_db_manager():
    if db_manager is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db_manager

# Dependency to get email processor
async def get_email_processor():
    if email_processor is None:
        raise HTTPException(status_code=500, detail="Email processor not initialized")
    return email_processor

# API Endpoints

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: DatabaseManager = Depends(get_db_manager)):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = db.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user_id = db.create_user(user.email, user.name)
        if not user_id:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return UserResponse(
            id=user_id,
            email=user.email,
            name=user.name,
            created_at=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_email}", response_model=UserResponse)
async def get_user(user_email: str, db: DatabaseManager = Depends(get_db_manager)):
    """Get user by email"""
    try:
        user = db.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/process-emails", response_model=EmailProcessingResponse)
async def process_emails(
    request: EmailProcessingRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_db_manager),
    processor: EmailProcessor = Depends(get_email_processor)
):
    """Process emails and extract relationships"""
    try:
        # Get or create user
        user = db.get_user_by_email(request.user_email)
        if not user:
            # Create user if doesn't exist
            user_id = db.create_user(request.user_email, request.user_email.split('@')[0])
            if not user_id:
                raise HTTPException(status_code=500, detail="Failed to create user")
        else:
            user_id = user['id']
        
        # Process emails in background
        background_tasks.add_task(
            process_emails_background,
            user_id,
            request.user_email,
            request.emails,
            db,
            processor
        )
        
        return EmailProcessingResponse(
            success=True,
            message="Email processing started",
            processing_stats={"total_emails": len(request.emails)},
            user_id=user_id
        )
        
    except Exception as e:
        logger.error(f"Error processing emails: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_emails_background(
    user_id: int,
    user_email: str,
    emails: List[Dict[str, Any]],
    db: DatabaseManager,
    processor: EmailProcessor
):
    """Background task to process emails"""
    try:
        logger.info(f"Starting background processing for user {user_email}")
        
        # Process emails
        processed_data = processor.process_emails(emails, user_email)
        
        # Store results in database
        await store_processing_results(user_id, processed_data, db)
        
        logger.info(f"Completed processing for user {user_email}")
        
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}")

async def store_processing_results(user_id: int, processed_data: Dict, db: DatabaseManager):
    """Store processing results in database"""
    try:
        # Create primary user person record
        primary_user_email = processed_data['user_email']
        primary_user_id = db.create_or_get_person(
            user_id=user_id,
            email=primary_user_email,
            name=primary_user_email.split('@')[0],
            is_primary_user=True
        )
        
        # Store companies
        company_id_map = {}
        for company in processed_data.get('companies', []):
            company_id = db.create_or_get_company(
                name=company.get('name', ''),
                domain=company.get('domain', ''),
                description=company.get('context', '')
            )
            if company_id:
                company_id_map[company.get('domain', company.get('name', ''))] = company_id
        
        # Store people
        person_id_map = {}
        for person in processed_data.get('people', []):
            person_email = person.get('email', '')
            if person_email and person_email != primary_user_email:  # Skip primary user
                company_id = None
                if person.get('company'):
                    company_domain = person.get('company', '').lower()
                    company_id = company_id_map.get(company_domain)
                
                person_id = db.create_or_get_person(
                    user_id=user_id,
                    email=person_email,
                    name=person.get('name', ''),
                    company_id=company_id,
                    role=person.get('role', '')
                )
                if person_id:
                    person_id_map[person_email] = person_id
        
        # Store interactions
        for interaction in processed_data.get('interactions', []):
            interaction_id = db.create_interaction(
                user_id=user_id,
                email_id=interaction.get('email_id', ''),
                thread_id=interaction.get('thread_id', ''),
                subject=interaction.get('subject', ''),
                interaction_date=datetime.strptime(interaction.get('interaction_date', ''), '%Y-%m-%d').date(),
                summary=interaction.get('interaction_summary', ''),
                full_content=interaction.get('full_content', ''),
                interaction_type=interaction.get('interaction_type', 'email')
            )
            
            if interaction_id:
                # Add participants (for now, just primary user)
                db.add_interaction_participant(
                    interaction_id=interaction_id,
                    person_id=primary_user_id,
                    role_in_interaction='primary_user'
                )
        
        # Store expertise
        expertise_id_map = {}
        for expertise_instance in processed_data.get('expertise_instances', []):
            expertise_name = expertise_instance.get('expertise_area', '')
            if expertise_name:
                expertise_id = db.get_or_create_expertise_area(
                    name=expertise_name,
                    description=f"Expertise in {expertise_name}"
                )
                if expertise_id:
                    expertise_id_map[expertise_name] = expertise_id
        
        # Mark emails as processed
        for email_id in processed_data.get('processed_emails', []):
            db.mark_email_processed(
                user_id=user_id,
                email_id=email_id,
                processed=True
            )
        
        # Mark filtered emails
        for email in processed_data.get('filtered_emails', []):
            db.mark_email_processed(
                user_id=user_id,
                email_id=email.get('id', ''),
                processed=False,
                filtered_out=True,
                filter_reason=email.get('_filter_reason', '')
            )
        
        logger.info(f"Stored processing results for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error storing processing results: {str(e)}")

@app.get("/users/{user_id}/relationships", response_model=List[RelationshipResponse])
async def get_user_relationships(
    user_id: int,
    limit: int = 100,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get relationships for a user"""
    try:
        relationships = db.get_person_relationships(user_id, limit)
        return [RelationshipResponse(**rel) for rel in relationships]
    except Exception as e:
        logger.error(f"Error getting relationships: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}/expertise", response_model=List[ExpertiseResponse])
async def get_user_expertise(
    user_id: int,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get expertise for all people associated with a user"""
    try:
        # This would need to be implemented in DatabaseManager
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Error getting expertise: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}/interactions", response_model=List[InteractionResponse])
async def get_user_interactions(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get interactions for a user within a date range"""
    try:
        if start_date and end_date:
            interactions = db.get_interactions_by_date_range(user_id, start_date, end_date)
        else:
            # Get all interactions (would need to implement this in DatabaseManager)
            interactions = []
        
        return [InteractionResponse(**inter) for inter in interactions[:limit]]
    except Exception as e:
        logger.error(f"Error getting interactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}/stats", response_model=ProcessingStatsResponse)
async def get_user_stats(
    user_id: int,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get processing statistics for a user"""
    try:
        stats = db.get_processing_stats(user_id)
        return ProcessingStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/upload-emails")
async def upload_emails(
    file: UploadFile = File(...),
    user_email: str = "",
    db: DatabaseManager = Depends(get_db_manager),
    processor: EmailProcessor = Depends(get_email_processor)
):
    """Upload emails from a JSON file"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and parse JSON file
        content = await file.read()
        emails = json.loads(content.decode('utf-8'))
        
        if not isinstance(emails, list):
            raise HTTPException(status_code=400, detail="Invalid JSON format - expected list of emails")
        
        # Process emails
        request = EmailProcessingRequest(
            user_email=user_email,
            emails=emails
        )
        
        return await process_emails(request, None, db, processor)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error uploading emails: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Email Relationship Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )