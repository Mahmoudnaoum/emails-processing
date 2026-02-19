"""
Populate demo tables with email data from last_1000_emails_full.json
Extracts people, companies, and interactions from emails
"""
import json
from retool_db_manager import RetoolDBManager
from datetime import datetime
import re


def extract_domain_from_email(email: str) -> str:
    """Extract domain from email address"""
    if '@' not in email:
        return None
    return email.split('@')[1].lower()


def extract_name_from_email(email: str) -> str:
    """Extract name from email address (part before @)"""
    if '@' not in email:
        return email
    return email.split('@')[0].replace('.', ' ').title()


def filter_newsletter_emails(email: dict) -> bool:
    """Filter out newsletter and notification emails"""
    from_email = email.get('From', '')
    subject = email.get('Subject', '')
    body = email.get('body', '').lower()
    
    # Newsletter patterns to exclude
    newsletter_patterns = [
        'unsubscribe', 'newsletter', 'notification', 'alert', 'update',
        'noreply', 'no-reply', 'donotreply', 'support@', 'info@',
        'digest', 'weekly', 'daily', 'subscription', 'billing@'
    ]
    
    # Check if any pattern matches
    for pattern in newsletter_patterns:
        if pattern in from_email.lower() or pattern in subject.lower() or pattern in body:
            return True
    
    return False


def extract_people_from_email(email: dict) -> list:
    """Extract people from email (from, to, cc, bcc)"""
    people = []
    
    # From field
    if 'From' in email:
        from_email = email['From']
        if from_email and '<' in from_email:
            # Extract email from angle brackets
            match = re.search(r'<([^>]+)>', from_email)
            if match:
                from_email = match.group(1)
        if from_email and '@' in from_email:
            people.append({
                'email': from_email,
                'name': extract_name_from_email(from_email)
            })
    
    # To field
    if 'To' in email:
        to_field = email['To']
        if isinstance(to_field, str):
            to_emails = [to_field]
        else:
            to_emails = to_field
        
        for to_email in to_emails:
            if '<' in to_email:
                # Extract email from angle brackets
                match = re.search(r'<([^>]+)>', to_email)
                if match:
                    to_email = match.group(1)
            if to_email and '@' in to_email:
                # Avoid duplicates
                if not any(p['email'] == to_email for p in people):
                    people.append({
                        'email': to_email,
                        'name': extract_name_from_email(to_email)
                    })
    
    return people


def populate_demo_tables(json_file: str, limit: int = None):
    """Populate demo tables with email data"""
    print("=" * 60)
    print("Populating Demo Tables from Email Data")
    print("=" * 60)
    
    # Load email data
    with open(json_file, 'r', encoding='utf-8') as f:
        emails = json.load(f)
    
    # Apply limit if specified
    if limit:
        emails = emails[:limit]
    
    print(f"\nProcessing {len(emails)} emails...")
    
    # Initialize database manager
    db = RetoolDBManager()
    
    if not db.connect():
        print("[ERROR] Failed to connect to database")
        return
    
    try:
        # Track statistics
        stats = {
            'processed': 0,
            'skipped': 0,
            'companies': 0,
            'people': 0,
            'interactions': 0
        }
        
        # Process each email
        for i, email in enumerate(emails):
            if (i + 1) % 100 == 0:
                print(f"\nProcessing {i + 1}/{len(emails)} emails...")
            
            # Filter out newsletters
            if filter_newsletter_emails(email):
                stats['skipped'] += 1
                continue
            
            # Extract people from email
            people = extract_people_from_email(email)
            
            if not people:
                stats['skipped'] += 1
                continue
            
            # Get or create company
            from_email = email['From']
            domain = extract_domain_from_email(from_email)
            company_id = None
            
            if domain:
                company_id = db.create_or_get_company(
                    name=domain.title(),
                    domain=domain,
                    description=f"Company with domain {domain}",
                    demo=True
                )
                if company_id:
                    stats['companies'] += 1
            
            # Create or get people
            person_ids = []
            for person in people:
                person_id = db.create_or_get_person(
                    user_id=1,  # Default user ID
                    email=person['email'],
                    name=person['name'],
                    company_id=company_id,
                    demo=True
                )
                if person_id:
                    person_ids.append(person_id)
                    stats['people'] += 1
            
            if not person_ids:
                stats['skipped'] += 1
                continue
            
            # Create interaction
            interaction_id = db.create_interaction(
                user_id=1,
                email_id=email.get('id', ''),
                thread_id=email.get('threadId', ''),
                subject=email.get('Subject', ''),
                summary=email.get('snippet', '')[:500] if email.get('snippet') else '',
                demo=True
            )
            
            if interaction_id:
                # Add participants
                for person_id in person_ids:
                    db.add_interaction_participant(
                        interaction_id=interaction_id,
                        person_id=person_id,
                        demo=True
                    )
                
                stats['interactions'] += 1
            
            # Mark email as processed
            db.mark_email_processed(
                user_id=1,
                email_id=email.get('id', ''),
                thread_id=email.get('threadId', ''),
                demo=True
            )
            
            stats['processed'] += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("Processing Complete!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Total emails processed: {stats['processed']}")
        print(f"  Emails skipped (newsletters): {stats['skipped']}")
        print(f"  Companies created: {stats['companies']}")
        print(f"  People created: {stats['people']}")
        print(f"  Interactions created: {stats['interactions']}")
        
        # Get final stats from database
        final_stats = db.get_stats(demo=True)
        print(f"\nFinal database stats:")
        print(f"  Companies: {final_stats.get('companies', 0)}")
        print(f"  People: {final_stats.get('people', 0)}")
        print(f"  Interactions: {final_stats.get('interactions', 0)}")
        print(f"  Expertise areas: {final_stats.get('expertise_areas', 0)}")
        print(f"  Processed emails: {final_stats.get('processed_emails', 0)}")
        
        db.close()
        
    except Exception as e:
        print(f"\n[ERROR] Failed to populate demo tables: {e}")
        db.close()


if __name__ == "__main__":
    # Default values
    json_file = "last_1000_emails_full.json"
    limit = 100  # Process first 100 emails by default
    
    # Parse command line arguments
    import sys
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            print(f"[ERROR] Invalid limit: {sys.argv[2]}")
            sys.exit(1)
    
    populate_demo_tables(json_file, limit)
