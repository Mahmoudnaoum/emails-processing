"""
Test script for the email relationship analysis system
"""

import json
import logging
from datetime import datetime
from email_processor import EmailProcessor
from database_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_processing():
    """Test the email processing system with sample data"""
    
    logger.info("Starting email processing test...")
    
    # Initialize components
    processor = EmailProcessor(llm_client=None)  # Without LLM for basic testing
    db_manager = DatabaseManager(db_type='sqlite')
    
    # Initialize database
    if not db_manager.initialize_database():
        logger.error("Failed to initialize database")
        return False
    
    # Load sample emails
    try:
        with open('last_1000_emails_full.json', 'r', encoding='utf-8') as f:
            emails = json.load(f)
    except FileNotFoundError:
        logger.error("Sample emails file not found")
        return False
    
    # Process first 10 emails for testing
    sample_emails = emails[:10]
    user_email = 'joseph@growthandcompany.com'
    
    logger.info(f"Processing {len(sample_emails)} emails for user {user_email}")
    
    # Process emails
    try:
        processed_data = processor.process_emails(sample_emails, user_email)
        
        # Display results
        logger.info("Processing completed successfully!")
        logger.info(f"Processed {len(processed_data['processed_emails'])} emails")
        logger.info(f"Found {len(processed_data['people'])} people")
        logger.info(f"Found {len(processed_data['companies'])} companies")
        logger.info(f"Found {len(processed_data['interactions'])} interactions")
        logger.info(f"Filtered {len(processed_data['filtered_emails'])} emails")
        
        # Store in database
        user_id = db_manager.create_user(user_email, 'Joseph Fitzgibbon')
        if not user_id:
            logger.error("Failed to create user")
            return False
        
        # Store companies
        company_id_map = {}
        for company in processed_data.get('companies', []):
            company_id = db_manager.create_or_get_company(
                name=company.get('name', ''),
                domain=company.get('domain', ''),
                description=company.get('context', '')
            )
            if company_id:
                company_id_map[company.get('domain', company.get('name', ''))] = company_id
                logger.info(f"Created company: {company.get('name', '')}")
        
        # Store people
        person_id_map = {}
        for person in processed_data.get('people', []):
            person_email = person.get('email', '')
            if person_email:
                company_id = None
                if person.get('company'):
                    company_domain = person.get('company', '').lower()
                    company_id = company_id_map.get(company_domain)
                
                person_id = db_manager.create_or_get_person(
                    user_id=user_id,
                    email=person_email,
                    name=person.get('name', ''),
                    company_id=company_id,
                    role=person.get('role', ''),
                    is_primary_user=(person_email == user_email)
                )
                if person_id:
                    person_id_map[person_email] = person_id
                    logger.info(f"Created person: {person.get('name', '')} ({person_email})")
        
        # Store interactions
        for interaction in processed_data.get('interactions', []):
            try:
                interaction_date = datetime.strptime(
                    interaction.get('interaction_date', ''), '%Y-%m-%d'
                ).date()
            except ValueError:
                interaction_date = datetime.now().date()
            
            interaction_id = db_manager.create_interaction(
                user_id=user_id,
                email_id=interaction.get('email_id', ''),
                thread_id=interaction.get('thread_id', ''),
                subject=interaction.get('subject', ''),
                interaction_date=interaction_date,
                summary=interaction.get('interaction_summary', ''),
                full_content=interaction.get('full_content', ''),
                interaction_type=interaction.get('interaction_type', 'email')
            )
            
            if interaction_id:
                logger.info(f"Created interaction: {interaction.get('subject', '')}")
        
        # Mark emails as processed
        for email_id in processed_data.get('processed_emails', []):
            db_manager.mark_email_processed(
                user_id=user_id,
                email_id=email_id,
                processed=True
            )
        
        # Test queries
        logger.info("\\nTesting database queries...")
        
        # Get processing stats
        stats = db_manager.get_processing_stats(user_id)
        logger.info(f"Processing stats: {stats}")
        
        # Get relationships
        relationships = db_manager.get_person_relationships(user_id, limit=5)
        logger.info(f"Found {len(relationships)} relationships")
        for rel in relationships[:3]:
            logger.info(f"  - {rel['person_name']} ↔ {rel['related_person_name']}: {rel['interaction_count']} interactions")
        
        logger.info("\\nTest completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        return False

def test_email_filtering():
    """Test the email filtering logic"""
    
    logger.info("Testing email filtering...")
    
    from email_filter import EmailFilter
    
    filter = EmailFilter()
    
    # Test emails
    test_emails = [
        {
            'From': 'newsletter@company.com',
            'To': 'user@example.com',
            'Subject': '[Newsletter] Weekly Update - Click here to unsubscribe',
            'body': 'This is our weekly newsletter with updates and promotions.'
        },
        {
            'From': 'colleague@company.com',
            'To': 'user@example.com',
            'Subject': 'Re: Project Discussion',
            'body': 'Hi, I wanted to follow up on our discussion about the project.'
        },
        {
            'From': 'noreply@google.com',
            'To': 'user@example.com',
            'Subject': 'Calendar invitation: Meeting tomorrow',
            'body': 'You have been invited to a meeting.'
        }
    ]
    
    for i, email in enumerate(test_emails):
        result = filter.should_filter_email(email)
        status = "FILTERED" if result.should_filter else "KEPT"
        logger.info(f"Email {i+1}: {status} - {result.reason}")
    
    logger.info("Email filtering test completed!")

def test_llm_prompts():
    """Test the LLM prompt templates"""
    
    logger.info("Testing LLM prompt templates...")
    
    from llm_prompts import LLMPromptTemplates
    
    templates = LLMPromptTemplates()
    
    # Sample email
    sample_email = {
        'From': 'joseph@growthandcompany.com',
        'To': 'luca@flashpack.com',
        'Cc': 'stefania@growthandcompany.com',
        'Subject': 'Re: Director role / Jan plan',
        'Date': 'Tue, 10 Feb 2026 15:32:00 +0000',
        'body': '''
        Hi Luca,
        
        I wanted to follow up on our discussion about the Director role. Based on our conversation, 
        I think we should focus on candidates with strong growth experience in the UK market.
        
        Let me know if you'd like to discuss this further.
        
        Best regards,
        Joseph
        '''
    }
    
    # Test people and companies extraction
    prompt = templates.extract_people_and_companies(sample_email)
    logger.info("People/Companies extraction prompt generated successfully")
    logger.info(f"Prompt length: {len(prompt)} characters")
    
    # Test interaction summary
    prompt = templates.extract_interaction_summary(sample_email)
    logger.info("Interaction summary prompt generated successfully")
    logger.info(f"Prompt length: {len(prompt)} characters")
    
    # Test expertise identification
    sample_people = [
        {'name': 'Joseph Fitzgibbon', 'email': 'joseph@growthandcompany.com', 'context': 'Sender discussing hiring'},
        {'name': 'Luca Grant-Snow', 'email': 'luca@flashpack.com', 'context': 'Recipient discussing role'}
    ]
    prompt = templates.identify_expertise(sample_email, sample_people)
    logger.info("Expertise identification prompt generated successfully")
    logger.info(f"Prompt length: {len(prompt)} characters")
    
    logger.info("LLM prompt templates test completed!")

if __name__ == "__main__":
    logger.info("Starting system tests...")
    
    # Run tests
    test_email_filtering()
    test_llm_prompts()
    test_email_processing()
    
    logger.info("All tests completed!")