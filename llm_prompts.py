"""
LLM prompt templates for extracting relationships, expertise, and interactions from emails
"""

from typing import Dict, List, Any
import json

class LLMPromptTemplates:
    
    @staticmethod
    def extract_people_and_companies(email_content: Dict) -> str:
        """
        Extract people and companies mentioned in an email
        """
        return f"""
You are an expert at analyzing emails to identify people and companies mentioned in business communications.

Analyze the following email and extract all people and companies mentioned:

EMAIL DETAILS:
From: {email_content.get('From', '')}
To: {email_content.get('To', '')}
Cc: {email_content.get('Cc', '')}
Subject: {email_content.get('Subject', '')}
Date: {email_content.get('Date', '')}

EMAIL BODY:
{email_content.get('body', '')}

Please extract the following information in JSON format:

{{
    "people": [
        {{
            "name": "Full name of person",
            "email": "email address if available",
            "role": "job title or role if mentioned",
            "company": "company they work for if mentioned",
            "confidence": 0.9,
            "context": "brief context of how they were mentioned"
        }}
    ],
    "companies": [
        {{
            "name": "Company name",
            "domain": "company domain if inferable from email",
            "confidence": 0.8,
            "context": "brief context of how company was mentioned"
        }}
    ]
}}

Guidelines:
1. Include the sender and all recipients
2. Look for people mentioned in the body (e.g., "John from Marketing said...")
3. Extract company names from email domains and mentions in text
4. Assign confidence scores (0.0-1.0) based on how certain you are
5. Only include people/companies with confidence > 0.5
6. Focus on business-related mentions, not casual references
"""

    @staticmethod
    def extract_interaction_summary(email_content: Dict) -> str:
        """
        Generate a summary of the interaction and identify key topics
        """
        return f"""
You are an expert at analyzing business emails to understand the core interaction and topics discussed.

Analyze the following email and provide a structured summary:

EMAIL DETAILS:
From: {email_content.get('From', '')}
To: {email_content.get('To', '')}
Cc: {email_content.get('Cc', '')}
Subject: {email_content.get('Subject', '')}
Date: {email_content.get('Date', '')}

EMAIL BODY:
{email_content.get('body', '')}

Please provide the following analysis in JSON format:

{{
    "interaction_summary": "Concise summary of what this email is about (1-2 sentences)",
    "key_topics": [
        {{
            "topic": "main topic discussed",
            "importance": "high/medium/low",
            "context": "brief context of how this topic was discussed"
        }}
    ],
    "interaction_type": "email/meeting/call/decision/inquiry/update/other",
    "action_items": [
        {{
            "action": "description of action item",
            "assigned_to": "person responsible if mentioned",
            "deadline": "deadline if mentioned"
        }}
    ],
    "business_context": "brief description of the business context (hiring, sales, partnership, etc.)",
    "sentiment": "positive/neutral/negative",
    "urgency": "high/medium/low"
}}

Guidelines:
1. Focus on business-relevant content
2. Extract concrete action items and responsibilities
3. Identify the primary business context
4. Assess the urgency and sentiment of the communication
5. Keep summaries concise but informative
"""

    @staticmethod
    def identify_expertise(email_content: Dict, people: List[Dict]) -> str:
        """
        Identify areas of expertise demonstrated by people in the email
        """
        people_context = "\n".join([f"- {p.get('name', '')}: {p.get('context', '')}" for p in people])
        
        return f"""
You are an expert at identifying areas of expertise demonstrated in business communications.

Analyze the following email and identify which people demonstrate expertise in specific areas:

EMAIL DETAILS:
From: {email_content.get('From', '')}
To: {email_content.get('To', '')}
Cc: {email_content.get('Cc', '')}
Subject: {email_content.get('Subject', '')}
Date: {email_content.get('Date', '')}

EMAIL BODY:
{email_content.get('body', '')}

PEOPLE IDENTIFIED:
{people_context}

Please identify expertise demonstrated in JSON format:

{{
    "expertise_instances": [
        {{
            "person_name": "name of person demonstrating expertise",
            "expertise_area": "area of expertise (e.g., hiring, growth, strategy, technology, marketing, finance, operations, sales, product, leadership)",
            "confidence": 0.8,
            "evidence": "specific text or behavior that demonstrates this expertise",
            "context": "how this expertise was applied in the interaction"
        }}
    ]
}}

Expertise areas to consider:
- hiring: Recruitment and talent acquisition
- growth: Business growth and scaling
- strategy: Strategic planning and business strategy
- technology: Technical expertise and software development
- marketing: Marketing and customer acquisition
- finance: Financial planning and investment
- operations: Business operations and management
- sales: Sales and business development
- product: Product development and management
- leadership: Leadership and team management

Guidelines:
1. Look for people providing advice, insights, or guidance
2. Identify who has the knowledge/expertise in each topic
3. Consider both explicit statements and implied expertise
4. Only assign expertise with confidence > 0.6
5. Focus on professional/business expertise, not general knowledge
"""

    @staticmethod
    def analyze_relationship_strength(email_content: Dict, interaction_history: List[Dict] = None) -> str:
        """
        Analyze the strength of relationships between people
        """
        history_context = ""
        if interaction_history:
            history_context = f"\n\nPREVIOUS INTERACTIONS:\n" + "\n".join([
                f"- {interaction.get('date', '')}: {interaction.get('summary', '')}" 
                for interaction in interaction_history[-5:]  # Last 5 interactions
            ])
        
        return f"""
You are an expert at analyzing business relationships and their strength based on email communications.

Analyze the following email to assess relationship strength:

EMAIL DETAILS:
From: {email_content.get('From', '')}
To: {email_content.get('To', '')}
Cc: {email_content.get('Cc', '')}
Subject: {email_content.get('Subject', '')}
Date: {email_content.get('Date', '')}

EMAIL BODY:
{email_content.get('body', '')}
{history_context}

Please provide relationship analysis in JSON format:

{{
    "relationship_assessments": [
        {{
            "person1": "first person in relationship",
            "person2": "second person in relationship",
            "relationship_strength": "strong/moderate/weak/unknown",
            "relationship_type": "professional/personal/mixed/client/partner/colleague",
            "confidence": 0.8,
            "evidence": "specific indicators of relationship strength",
            "interaction_frequency": "high/medium/low/unknown",
            "trust_level": "high/medium/low/unknown",
            "formality": "formal/informal/mixed"
        }}
    ]
}}

Guidelines:
1. Assess relationship strength based on tone, familiarity, and context
2. Look for indicators of trust, history, and rapport
3. Consider formality level and communication style
4. Factor in interaction frequency if history is available
5. Focus on business relationships
6. Only assess relationships with confidence > 0.6
"""

    @staticmethod
    def extract_interaction_participants(email_content: Dict, people: List[Dict]) -> str:
        """
        Identify the role of each participant in the interaction
        """
        people_list = "\n".join([f"- {p.get('name', '')} ({p.get('email', '')})" for p in people])
        
        return f"""
You are an expert at analyzing email interactions to understand each participant's role.

Analyze the following email and identify each person's role in the interaction:

EMAIL DETAILS:
From: {email_content.get('From', '')}
To: {email_content.get('To', '')}
Cc: {email_content.get('Cc', '')}
Subject: {email_content.get('Subject', '')}
Date: {email_content.get('Date', '')}

EMAIL BODY:
{email_content.get('body', '')}

PEOPLE INVOLVED:
{people_list}

Please identify participant roles in JSON format:

{{
    "participant_roles": [
        {{
            "person_name": "name of person",
            "role_in_interaction": "sender/recipient/expert/requester/decision_maker/informed/cc/bcc",
            "is_expert": true/false,
            "expertise_area": "area of expertise if they are the expert",
            "contribution": "brief description of their contribution to the interaction",
            "influence_level": "high/medium/low",
            "confidence": 0.9
        }}
    ]
}}

Role definitions:
- sender: Person who wrote the email
- recipient: Primary recipient actively involved in discussion
- expert: Person providing expertise or guidance
- requester: Person asking for something or making a request
- decision_maker: Person making or influencing decisions
- informed: Person being kept informed but not actively participating
- cc/bcc: Person copied for awareness

Guidelines:
1. Identify who is driving the conversation
2. Look for expertise being demonstrated
3. Assess each person's influence on the outcome
4. Consider both explicit and implicit roles
5. Only assign roles with confidence > 0.7
"""

    @staticmethod
    def generate_thread_summary(thread_emails: List[Dict]) -> str:
        """
        Generate a comprehensive summary of an entire email thread
        """
        thread_context = "\n\n".join([
            f"EMAIL {i+1}:\nFrom: {email.get('From', '')}\nDate: {email.get('Date', '')}\nSubject: {email.get('Subject', '')}\nBody: {email.get('body', '')[:500]}..."
            for i, email in enumerate(thread_emails)
        ])
        
        return f"""
You are an expert at analyzing email threads to understand the complete conversation and relationships.

Analyze the following email thread and provide a comprehensive summary:

EMAIL THREAD:
{thread_context}

Please provide a thread analysis in JSON format:

{{
    "thread_summary": "Comprehensive summary of the entire thread (2-3 sentences)",
    "participants": [
        {{
            "name": "person name",
            "role": "primary/secondary/expert/requester/decision_maker",
            "contribution": "summary of their role in the thread",
            "expertise_demonstrated": ["areas of expertise if any"]
        }}
    ],
    "key_topics": [
        {{
            "topic": "main topic",
            "evolution": "how the topic evolved through the thread",
            "resolution": "how the topic was resolved or current status"
        }}
    ],
    "decisions_made": [
        {{
            "decision": "description of decision",
            "made_by": "who made the decision",
            "impact": "impact of the decision"
        }}
    ],
    "action_items": [
        {{
            "action": "description of action item",
            "assigned_to": "person responsible",
            "status": "pending/completed/in_progress",
            "deadline": "deadline if mentioned"
        }}
    ],
    "relationship_dynamics": "description of how relationships evolved or were demonstrated in this thread",
    "business_outcome": "business result or next step from this thread"
}}

Guidelines:
1. Track how the conversation evolved over multiple emails
2. Identify key decision points and who influenced them
3. Look for relationship building or strengthening moments
4. Extract concrete outcomes and next steps
5. Consider the business context and implications
6. Focus on actionable insights and relationship development
"""

    @staticmethod
    def extract_company_relationships(email_content: Dict, companies: List[Dict]) -> str:
        """
        Extract relationships between companies mentioned in the email
        """
        companies_list = "\n".join([f"- {c.get('name', '')} ({c.get('domain', '')})" for c in companies])
        
        return f"""
You are an expert at analyzing business communications to understand company relationships.

Analyze the following email and identify relationships between companies:

EMAIL DETAILS:
From: {email_content.get('From', '')}
To: {email_content.get('To', '')}
Cc: {email_content.get('Cc', '')}
Subject: {email_content.get('Subject', '')}
Date: {email_content.get('Date', '')}

EMAIL BODY:
{email_content.get('body', '')}

COMPANIES MENTIONED:
{companies_list}

Please identify company relationships in JSON format:

{{
    "company_relationships": [
        {{
            "company1": "first company name",
            "company2": "second company name",
            "relationship_type": "client/supplier/partner/competitor/acquirer/acquired/parent/subsidiary/colleague",
            "relationship_context": "description of how these companies are related",
            "confidence": 0.8,
            "business_nature": "nature of business between these companies"
        }}
    ]
}}

Relationship types:
- client: One company is a client of the other
- supplier: One company supplies goods/services to the other
- partner: Companies are working together in partnership
- competitor: Companies are competitors in the market
- acquirer/acquired: One company acquired the other
- parent/subsidiary: Parent-subsidiary relationship
- colleague: Companies working together as equals

Guidelines:
1. Look for explicit mentions of business relationships
2. Infer relationships from context and business discussions
3. Consider the nature of interactions between company representatives
4. Only assign relationships with confidence > 0.6
5. Focus on active business relationships
"""