"""
Simplified Email Processor for Retool Integration
Processes emails and stores relationships directly in Retool database
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from email_filter import EmailFilter
from llm_prompts import LLMPrompts
from retool_db_manager import RetoolDBManager


class RetoolEmailProcessor:
    """Simplified email processor for Retool integration"""

    def __init__(self, db_manager: RetoolDBManager = None):
        """Initialize the processor"""
        self.db = db_manager or RetoolDBManager()
        self.filter = EmailFilter()
        self.prompts = LLMPrompts()

    def load_emails(self, json_file: str) -> List[Dict]:
        """Load emails from JSON file"""
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_domain(self, email: str) -> Optional[str]:
        """Extract domain from email address"""
        if '@' in email:
            return email.split('@')[1].lower()
        return None

    def extract_company_name(self, domain: str) -> str:
        """Extract company name from domain"""
        if not domain:
            return "Unknown"
        # Remove common TLDs and get the main domain
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[-2].capitalize()
        return domain.capitalize()

    def process_email(self, email: Dict) -> Optional[Dict]:
        """Process a single email and extract relationships"""
        # Check if already processed
        email_id = email.get('id')
        if self.db.is_email_processed(email_id):
            return None

        # Filter out newsletters/notifications
        subject = email.get('subject', '')
        sender = email.get('sender', '')
        sender_email = sender.get('email', '') if isinstance(sender, dict) else sender

        if self.filter.is_newsletter_or_notification(subject, sender_email):
            return {'filtered': True, 'email_id': email_id}

        # Extract email content
        headers = email.get('payload', {}).get('headers', [])
        from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
        to_headers = [h['value'] for h in headers if h['name'] == 'To']
        cc_headers = [h['value'] for h in headers if h['name'] == 'Cc']

        # Parse email addresses
        participants = self._parse_email_addresses([from_header] + to_headers + cc_headers)

        # Extract company info from sender
        sender_domain = self.extract_domain(sender_email)
        company_name = self.extract_company_name(sender_domain)

        # Create or get company
        company_id = self.db.create_or_get_company(company_name, sender_domain)

        # Create or get people
        person_ids = []
        for participant in participants:
            person_id = self.db.create_or_get_person(
                email=participant['email'],
                name=participant['name'],
                company_id=company_id if participant['email'] == sender_email else None
            )
            person_ids.append(person_id)

        # Generate LLM prompt for relationship extraction
        prompt = self.prompts.generate_relationship_prompt(
            subject=subject,
            body=email.get('snippet', ''),
            sender=sender_email,
            recipients=', '.join([p['email'] for p in participants if p['email'] != sender_email])
        )

        # Parse email date
        email_date = None
        date_str = email.get('internalDate')
        if date_str:
            try:
                email_date = datetime.fromtimestamp(int(date_str) / 1000)
            except:
                pass

        # Create interaction
        interaction_id = self.db.create_interaction(
            email_id=email_id,
            thread_id=email.get('threadId'),
            subject=subject,
            summary=email.get('snippet', '')[:500],  # Truncate summary
            interaction_date=email_date
        )

        # Add participants to interaction
        for person_id in person_ids:
            self.db.add_interaction_participant(interaction_id, person_id)

        # Mark email as processed
        self.db.mark_email_processed(email_id)

        return {
            'processed': True,
            'email_id': email_id,
            'subject': subject,
            'participants': len(participants),
            'company': company_name
        }

    def _parse_email_addresses(self, email_strings: List[str]) -> List[Dict]:
        """Parse email addresses from strings"""
        participants = []
        seen_emails = set()

        for email_str in email_strings:
            if not email_str:
                continue

            # Handle comma-separated emails
            emails = [e.strip() for e in email_str.split(',')]

            for email in emails:
                if not email or email in seen_emails:
                    continue

                # Parse "Name <email@example.com>" format
                name = None
                email_addr = email

                if '<' in email and '>' in email:
                    name = email.split('<')[0].strip().strip('"\'')
                    email_addr = email.split('<')[1].split('>')[0].strip()

                # Clean name
                if name and name == email_addr:
                    name = None

                participants.append({
                    'email': email_addr,
                    'name': name
                })
                seen_emails.add(email_addr)

        return participants

    def process_emails(self, json_file: str, limit: int = None) -> Dict:
        """Process all emails from a JSON file"""
        if not self.db.connect():
            return {'error': 'Failed to connect to database'}

        try:
            emails = self.load_emails(json_file)
            if limit:
                emails = emails[:limit]

            results = {
                'total': len(emails),
                'processed': 0,
                'filtered': 0,
                'errors': 0,
                'details': []
            }

            for email in emails:
                try:
                    result = self.process_email(email)
                    if result:
                        if result.get('filtered'):
                            results['filtered'] += 1
                        else:
                            results['processed'] += 1
                            results['details'].append(result)
                except Exception as e:
                    print(f"Error processing email {email.get('id')}: {e}")
                    results['errors'] += 1

            return results

        finally:
            self.db.close()

    def add_expertise(self, person_email: str, expertise_name: str, description: str = None):
        """Add expertise to a person"""
        if not self.db.connect():
            return {'error': 'Failed to connect to database'}

        try:
            # Get person by email
            result = self.db.execute_query(
                "SELECT id FROM people WHERE email = %s",
                (person_email,)
            )
            if not result:
                return {'error': 'Person not found'}

            person_id = result[0]['id']

            # Get or create expertise
            expertise_id = self.db.get_or_create_expertise(expertise_name, description)

            # Add expertise to person
            self.db.add_expertise_to_person(person_id, expertise_id)

            return {'success': True, 'person_id': person_id, 'expertise_id': expertise_id}

        finally:
            self.db.close()
