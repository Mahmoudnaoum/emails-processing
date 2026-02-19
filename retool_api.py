"""
Simple API for Retool Integration
FastAPI endpoints to interact with the email processing system
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from retool_db_manager import RetoolDBManager
from retool_email_processor import RetoolEmailProcessor
import os

app = FastAPI(title="Retool Email Processing API")

# CORS middleware for Retool
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Retool domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database manager instance
db = RetoolDBManager()

# Pydantic models
class ExpertiseRequest(BaseModel):
    person_email: str
    expertise_name: str
    description: Optional[str] = None


class ProcessEmailsRequest(BaseModel):
    json_file: str
    limit: Optional[int] = None


# Health check
@app.get("/")
def health_check():
    """Health check endpoint"""
    if db.connect():
        stats = db.get_stats()
        db.close()
        return {"status": "healthy", "database": "connected", "stats": stats}
    return {"status": "unhealthy", "database": "disconnected"}


# Companies endpoints
@app.get("/companies")
def get_companies():
    """Get all companies"""
    if db.connect():
        try:
            companies = db.get_companies()
            return {"success": True, "companies": companies}
        finally:
            db.close()
    raise HTTPException(status_code=500, detail="Database connection failed")


# People endpoints
@app.get("/people")
def get_people():
    """Get all people with company info"""
    if db.connect():
        try:
            people = db.get_people()
            return {"success": True, "people": people}
        finally:
            db.close()
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/people/{person_id}/expertise")
def get_person_expertise(person_id: int):
    """Get expertise for a specific person"""
    if db.connect():
        try:
            expertise = db.get_person_expertise(person_id)
            return {"success": True, "expertise": expertise}
        finally:
            db.close()
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.post("/people/expertise")
def add_expertise(request: ExpertiseRequest):
    """Add expertise to a person"""
    processor = RetoolEmailProcessor(db)
    result = processor.add_expertise(
        person_email=request.person_email,
        expertise_name=request.expertise_name,
        description=request.description
    )
    if result.get('error'):
        raise HTTPException(status_code=400, detail=result['error'])
    return {"success": True, "data": result}


# Interactions endpoints
@app.get("/interactions")
def get_interactions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get interactions with optional date filtering"""
    if db.connect():
        try:
            interactions = db.get_interactions(start_date, end_date)
            return {"success": True, "interactions": interactions}
        finally:
            db.close()
    raise HTTPException(status_code=500, detail="Database connection failed")


# Processing endpoints
@app.post("/process-emails")
def process_emails(request: ProcessEmailsRequest):
    """Process emails from JSON file"""
    processor = RetoolEmailProcessor(db)
    result = processor.process_emails(request.json_file, request.limit)
    if result.get('error'):
        raise HTTPException(status_code=500, detail=result['error'])
    return {"success": True, "result": result}


# Stats endpoint
@app.get("/stats")
def get_stats():
    """Get database statistics"""
    if db.connect():
        try:
            stats = db.get_stats()
            return {"success": True, "stats": stats}
        finally:
            db.close()
    raise HTTPException(status_code=500, detail="Database connection failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
