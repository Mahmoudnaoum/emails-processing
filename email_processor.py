"""
Main email processing pipeline for extracting relationships, expertise, and interactions
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
import re
from email.utils import parseaddr
from email_filter import EmailFilter, FilterResult
from llm_prompts import LLMPromptTemplates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self, llm_client=None):
        """
        Initialize the email processor
        
        Args:
            llm_client: Client for making LLM API calls (OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
        self.email_filter = EmailFilter()
        self.prompt_templates = LLMPromptTemplates()
        
        # Cache for processed data to avoid duplicate processing
        self.people_cache = {}
        self.companies_cache = {}
        self.expertise_cache = {}
    
    def process_emails(self, emails: List[Dict], user_email: str) -> Dict[str, Any]:
        """
        Process a list of emails and extract relationships, expertise, and interactions
        
        Args:
            emails: List of email dictionaries
            user_email: Email address of the primary user
            
        Returns:
            Dictionary containing processed data
        """
        logger.info(f"Processing {len(emails)} emails for user {user_email}")
        
        # Step 1: Filter out newsletters and notifications
        kept_emails, filtered_emails = self.email_filter.filter_emails(emails)
        logger.info(f"Filtered {len(filtered_emails)} emails, keeping {len(kept_emails)}")
        
        # Step 2: Group emails by thread for better context
        threaded_emails = self._group_by_thread(kept_emails)
        
        # Step 3: Process each email/thread
        processed_data = {
            'user_email': user_email,
            'processed_emails': [],
            'people': {},
            'companies': {},
            'interactions': [],
            'expertise_instances': [],
            'filtered_emails': filtered_emails,
            'processing_stats': {
                'total_emails': len(emails),
                'kept_emails': len(kept_emails),
                'filtered_emails': len(filtered_emails),
                'threads_processed': len(threaded_emails)
            }
        }
        
        for thread_id, thread_emails in threaded_emails.items():
            try:
                thread_result = self._process_thread(thread_emails, user_email)
                self._merge_thread_result(processed_data, thread_result)
            except Exception as e:
                logger.error(f"Error processing thread {thread_id}: {str(e)}")
                continue
        
        # Step 4: Post-process and clean up data
        self._post_process_data(processed_data)
        
        logger.info(f"Processing complete. Found {len(processed_data['people'])} people, "
                   f"{len(processed_data['companies'])} companies, {len(processed_data['interactions'])} interactions")
        
        return processed_data
    
    def _group_by_thread(self, emails: List[Dict]) -> Dict[str, List[Dict]]:
        """Group emails by thread ID"""
        threads = {}
        for email in emails:
            thread_id = email.get('threadId', email.get('id'))
            if thread_id not in threads:
                threads[thread_id] = []
            threads[thread_id].append(email)
        
        # Sort emails within each thread by date
        for thread_id in threads:
            threads[thread_id].sort(key=lambda x: self._parse_date(x.get('Date', '')))
        
        return threads
    
    def _process_thread(self, thread_emails: List[Dict], user_email: str) -> Dict[str, Any]:
        """Process a single email thread"""
        if len(thread_emails) == 1:
            return self._process_single_email(thread_emails[0], user_email)
        else:
            return self._process_multi_email_thread(thread_emails, user_email)
    
    def _process_single_email(self, email: Dict, user_email: str) -> Dict[str, Any]:
        """Process a single email"""
        email_id = email.get('id')
        
        # Extract people and companies
        people_result = self._extract_people_and_companies(email)
        
        # Generate interaction summary
        interaction_result = self._extract_interaction_summary(email)
        
        # Identify expertise
        expertise_result = self._identify_expertise(email, people_result['people'])
        
        # Analyze participant roles
        roles_result = self._extract_participant_roles(email, people_result['people'])
        
        return {
            'emails_processed': [email_id],
            'people': people_result['people'],
            'companies': people_result['companies'],
            'interactions': [interaction_result],
            'expertise_instances': expertise_result['expertise_instances'],
            'participant_roles': roles_result['participant_roles']
        }
    
    def _process_multi_email_thread(self, thread_emails: List[Dict], user_email: str) -> Dict[str, Any]:
        """Process a multi-email thread"""
        # Generate thread summary
        thread_summary = self._generate_thread_summary(thread_emails)
        
        # Process each individual email for detailed analysis
        all_people = {}
        all_companies = {}
        all_interactions = []
        all_expertise = []
        all_roles = []
        
        for email in thread_emails:
            # Extract people and companies
            people_result = self._extract_people_and_companies(email)
            for person in people_result['people']:
                email_key = person.get('email', person.get('name', ''))
                if email_key and email_key not in all_people:
                    all_people[email_key] = person
            
            for company in people_result['companies']:
                company_key = company.get('domain', company.get('name', ''))
                if company_key and company_key not in all_companies:
                    all_companies[company_key] = company
            
            # Generate individual interaction summary
            interaction_result = self._extract_interaction_summary(email)
            all_interactions.append(interaction_result)
            
            # Identify expertise
            expertise_result = self._identify_expertise(email, list(all_people.values()))
            all_expertise.extend(expertise_result['expertise_instances'])
            
            # Extract participant roles
            roles_result = self._extract_participant_roles(email, list(all_people.values()))
            all_roles.extend(roles_result['participant_roles'])
        
        return {
            'emails_processed': [email.get('id') for email in thread_emails],
            'people': list(all_people.values()),
            'companies': list(all_companies.values()),
            'interactions': all_interactions,
            'expertise_instances': all_expertise,
            'participant_roles': all_roles,
            'thread_summary': thread_summary
        }
    
    def _extract_people_and_companies(self, email: Dict) -> Dict:
        """Extract people and companies from an email"""
        if not self.llm_client:
            # Fallback to basic extraction without LLM
            return self._basic_people_company_extraction(email)
        
        prompt = self.prompt_templates.extract_people_and_companies(email)
        response = self._call_llm(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response for people/companies extraction")
            return self._basic_people_company_extraction(email)
    
    def _extract_interaction_summary(self, email: Dict) -> Dict:
        """Generate interaction summary"""
        if not self.llm_client:
            return self._basic_interaction_summary(email)
        
        prompt = self.prompt_templates.extract_interaction_summary(email)
        response = self._call_llm(prompt)
        
        try:
            result = json.loads(response)
            result['email_id'] = email.get('id')
            result['thread_id'] = email.get('threadId')
            result['subject'] = email.get('Subject', '')
            result['interaction_date'] = self._parse_date(email.get('Date', '')).date().isoformat()
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response for interaction summary")
            return self._basic_interaction_summary(email)
    
    def _identify_expertise(self, email: Dict, people: List[Dict]) -> Dict:
        """Identify expertise demonstrated in the email"""
        if not self.llm_client or not people:
            return {'expertise_instances': []}
        
        prompt = self.prompt_templates.identify_expertise(email, people)
        response = self._call_llm(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response for expertise identification")
            return {'expertise_instances': []}
    
    def _extract_participant_roles(self, email: Dict, people: List[Dict]) -> Dict:
        """Extract participant roles in the interaction"""
        if not self.llm_client or not people:
            return {'participant_roles': []}
        
        prompt = self.prompt_templates.extract_interaction_participants(email, people)
        response = self._call_llm(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response for participant roles")
            return {'participant_roles': []}
    
    def _generate_thread_summary(self, thread_emails: List[Dict]) -> Dict:
        """Generate thread summary"""
        if not self.llm_client:
            return {'thread_summary': 'Thread summary not available without LLM'}
        
        prompt = self.prompt_templates.generate_thread_summary(thread_emails)
        response = self._call_llm(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response for thread summary")
            return {'thread_summary': 'Failed to generate thread summary'}
    
    def _basic_people_company_extraction(self, email: Dict) -> Dict:
        """Basic extraction without LLM"""
        people = []
        companies = []
        
        # Extract from headers
        for field in ['From', 'To', 'Cc', 'Bcc']:
            if field in email:
                field_people = self._parse_email_addresses(email[field])
                people.extend(field_people)
        
        # Extract companies from email domains
        for person in people:
            if 'email' in person:
                domain = self._extract_domain(person['email'])
                if domain:
                    companies.append({
                        'name': domain.split('.')[0].title(),
                        'domain': domain,
                        'confidence': 0.7,
                        'context': f"Extracted from {person['name']}'s email address"
                    })
        
        return {'people': people, 'companies': companies}
    
    def _basic_interaction_summary(self, email: Dict) -> Dict:
        """Basic interaction summary without LLM"""
        return {
            'email_id': email.get('id'),
            'thread_id': email.get('threadId'),
            'subject': email.get('Subject', ''),
            'interaction_summary': email.get('snippet', ''),
            'key_topics': [],
            'interaction_type': 'email',
            'action_items': [],
            'business_context': 'unknown',
            'sentiment': 'neutral',
            'urgency': 'medium',
            'interaction_date': self._parse_date(email.get('Date', '')).date().isoformat()
        }
    
    def _parse_email_addresses(self, address_string: str) -> List[Dict]:
        """Parse email addresses and extract names"""
        addresses = []
        for addr in address_string.split(','):
            name, email = parseaddr(addr.strip())
            if email:
                addresses.append({
                    'name': name if name else email.split('@')[0],
                    'email': email,
                    'confidence': 0.9,
                    'context': f"Found in email headers"
                })
        return addresses
    
    def _extract_domain(self, email_address: str) -> str:
        """Extract domain from email address"""
        match = re.search(r'@([^>]+)', email_address)
        if match:
            return match.group(1).lower()
        return ""
    
    def _parse_date(self, date_string: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            # Try various date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%d %b %Y %H:%M:%S %z',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            # Fallback to current date if parsing fails
            return datetime.now()
        except Exception:
            return datetime.now()
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM API - to be implemented based on specific LLM service"""
        if not self.llm_client:
            return '{"error": "No LLM client configured"}'
        
        # This should be implemented based on the specific LLM service being used
        # For example, OpenAI, Anthropic, or local LLM
        try:
            response = self.llm_client.generate(prompt)
            return response
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            return '{"error": "LLM API call failed"}'
    
    def _merge_thread_result(self, processed_data: Dict, thread_result: Dict):
        """Merge thread processing results into main processed data"""
        # Merge people
        for person in thread_result.get('people', []):
            key = person.get('email', person.get('name', ''))
            if key and key not in processed_data['people']:
                processed_data['people'][key] = person
        
        # Merge companies
        for company in thread_result.get('companies', []):
            key = company.get('domain', company.get('name', ''))
            if key and key not in processed_data['companies']:
                processed_data['companies'][key] = company
        
        # Merge interactions
        processed_data['interactions'].extend(thread_result.get('interactions', []))
        
        # Merge expertise instances
        processed_data['expertise_instances'].extend(thread_result.get('expertise_instances', []))
        
        # Merge processed emails
        processed_data['processed_emails'].extend(thread_result.get('emails_processed', []))
    
    def _post_process_data(self, processed_data: Dict):
        """Clean up and organize processed data"""
        # Convert people dict to list
        processed_data['people'] = list(processed_data['people'].values())
        
        # Convert companies dict to list
        processed_data['companies'] = list(processed_data['companies'].values())
        
        # Remove duplicates and sort by confidence
        processed_data['people'] = self._deduplicate_list(processed_data['people'], 'email')
        processed_data['companies'] = self._deduplicate_list(processed_data['companies'], 'domain')
        processed_data['expertise_instances'] = self._deduplicate_list(processed_data['expertise_instances'], None)
        
        # Sort by confidence (descending)
        for key in ['people', 'companies', 'expertise_instances']:
            processed_data[key] = sorted(processed_data[key], 
                                       key=lambda x: x.get('confidence', 0), 
                                       reverse=True)
    
    def _deduplicate_list(self, items: List[Dict], key_field: str) -> List[Dict]:
        """Remove duplicates from a list based on a key field"""
        seen = set()
        unique_items = []
        
        for item in items:
            if key_field:
                key = item.get(key_field)
                if key and key not in seen:
                    seen.add(key)
                    unique_items.append(item)
            else:
                # For items without a clear key, use a tuple of values
                key_tuple = tuple(sorted(item.items()))
                if key_tuple not in seen:
                    seen.add(key_tuple)
                    unique_items.append(item)
        
        return unique_items

# Example usage
if __name__ == "__main__":
    # This would be used with an actual LLM client
    processor = EmailProcessor(llm_client=None)
    
    # Load sample emails
    with open('last_1000_emails_full.json', 'r') as f:
        emails = json.load(f)
    
    # Process first 10 emails as example
    sample_emails = emails[:10]
    result = processor.process_emails(sample_emails, 'joseph@growthandcompany.com')
    
    print(f"Processed {len(result['processed_emails'])} emails")
    print(f"Found {len(result['people'])} people and {len(result['companies'])} companies")
    print(f"Identified {len(result['interactions'])} interactions")
    print(f"Found {len(result['expertise_instances'])} expertise instances")