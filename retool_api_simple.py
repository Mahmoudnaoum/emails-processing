"""
Simple API for Retool Integration
Flask-based API (no pydantic required)
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, List, Optional
from datetime import date
from retool_db_manager import RetoolDBManager
from retool_email_processor import RetoolEmailProcessor
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Retool

# Database manager instance
db = RetoolDBManager()


@app.route('/')
def health_check():
    """Health check endpoint"""
    if db.connect():
        stats = db.get_stats()
        db.close()
        return jsonify({"status": "healthy", "database": "connected", "stats": stats})
    return jsonify({"status": "unhealthy", "database": "disconnected"})


@app.route('/companies', methods=['GET'])
def get_companies():
    """Get all companies"""
    if db.connect():
        try:
            companies = db.get_companies()
            return jsonify({"success": True, "companies": companies})
        finally:
            db.close()
    return jsonify({"success": False, "error": "Database connection failed"}), 500


@app.route('/people', methods=['GET'])
def get_people():
    """Get all people with company info"""
    if db.connect():
        try:
            people = db.get_people()
            return jsonify({"success": True, "people": people})
        finally:
            db.close()
    return jsonify({"success": False, "error": "Database connection failed"}), 500


@app.route('/people/<int:person_id>/expertise', methods=['GET'])
def get_person_expertise(person_id: int):
    """Get expertise for a specific person"""
    if db.connect():
        try:
            expertise = db.get_person_expertise(person_id)
            return jsonify({"success": True, "expertise": expertise})
        finally:
            db.close()
    return jsonify({"success": False, "error": "Database connection failed"}), 500


@app.route('/people/expertise', methods=['POST'])
def add_expertise():
    """Add expertise to a person"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    person_email = data.get('person_email')
    expertise_name = data.get('expertise_name')
    description = data.get('description')
    
    if not person_email or not expertise_name:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    processor = RetoolEmailProcessor(db)
    result = processor.add_expertise(person_email, expertise_name, description)
    
    if result.get('error'):
        return jsonify({"success": False, "error": result['error']}), 400
    
    return jsonify({"success": True, "data": result})


@app.route('/interactions', methods=['GET'])
def get_interactions():
    """Get interactions with optional date filtering"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Convert date strings to date objects
    start = None
    end = None
    if start_date:
        try:
            start = date.fromisoformat(start_date)
        except:
            pass
    if end_date:
        try:
            end = date.fromisoformat(end_date)
        except:
            pass
    
    if db.connect():
        try:
            interactions = db.get_interactions(start, end)
            return jsonify({"success": True, "interactions": interactions})
        finally:
            db.close()
    return jsonify({"success": False, "error": "Database connection failed"}), 500


@app.route('/process-emails', methods=['POST'])
def process_emails():
    """Process emails from JSON file"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    json_file = data.get('json_file')
    limit = data.get('limit')
    
    if not json_file:
        return jsonify({"success": False, "error": "Missing json_file field"}), 400
    
    processor = RetoolEmailProcessor(db)
    result = processor.process_emails(json_file, limit)
    
    if result.get('error'):
        return jsonify({"success": False, "error": result['error']}), 500
    
    return jsonify({"success": True, "result": result})


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    if db.connect():
        try:
            stats = db.get_stats()
            return jsonify({"success": True, "stats": stats})
        finally:
            db.close()
    return jsonify({"success": False, "error": "Database connection failed"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
