"""
Email filtering logic to identify and exclude newsletters, notifications, and automated messages
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class FilterResult:
    should_filter: bool
    reason: str
    confidence: float  # 0.0 to 1.0

class EmailFilter:
    def __init__(self):
        # Patterns that indicate newsletters/notifications
        self.newsletter_patterns = [
            r'unsubscribe',
            r'newsletter',
            r'daily digest',
            r'weekly digest',
            r'marketing',
            r'promotion',
            r'sale',
            r'discount',
            r'offer',
            r'deal',
            r'subscription',
            r'update.*notification',
            r'notification.*update',
            r'alert',
            r'reminder',
            r'invitation.*accepted',
            r'registration.*approved',
            r'calendar.*notification',
            r'meeting.*invitation',
            r'event.*reminder'
        ]
        
        # Patterns that indicate automated/system emails
        self.automated_patterns = [
            r'noreply@',
            r'no-reply@',
            r'do-not-reply@',
            r'notification@',
            r'alerts@',
            r'mailer@',
            r'digest@',
            r'updates@',
            r'calendar@',
            r'meetings@',
            r'invitations@',
            r'team@',
            r'support@',
            r'billing@',
            r'account@',
            r'security@',
            r'privacy@',
            r'legal@',
            r'abuse@',
            r'postmaster@',
            r'admin@'
        ]
        
        # Subject patterns to filter
        self.subject_filter_patterns = [
            r'^\s*\[.*\]\s*',  # Square bracket prefixes like [Newsletter]
            r'^\s*Re:\s*\[.*\]\s*',  # Re: [Newsletter]
            r'^\s*Fwd:\s*\[.*\]\s*',  # Fwd: [Newsletter]
            r'Your .* statement',
            r'Your .* receipt',
            r'Your .* invoice',
            r'Your .* order',
            r'Your .* subscription',
            r'Your .* account',
            r'Your .* password',
            r'Your .* verification',
            r'Your .* confirmation',
            r'Your .* registration',
            r'Your .* booking',
            r'Your .* reservation',
            r'Payment.*received',
            r'Transaction.*complete',
            r'Order.*shipped',
            r'Delivery.*update',
            r'Package.*tracking',
            r'Shipping.*notification',
            r'Appointment.*reminder',
            r'Meeting.*reminder',
            r'Calendar.*invitation',
            r'Event.*invitation',
            r'You.*been.*invited',
            r'You.*been.*added',
            r'You.*been.*mentioned',
            r'Welcome to',
            r'Thank you for',
            r'Confirm your',
            r'Verify your',
            r'Update your',
            r'Change your',
            r'Reset your',
            r'Your.*has been',
            r'Your.*have been',
            r'Your.*was',
            r'Your.*were',
            r'Important notice',
            r'Action required',
            r'Urgent.*required',
            r'Security.*alert',
            r'Privacy.*update',
            r'Terms.*update',
            r'Policy.*update'
        ]
        
        # Body patterns that indicate automated content
        self.body_filter_patterns = [
            r'click here to unsubscribe',
            r'unsubscribe.*here',
            r'opt out.*here',
            r'preferences.*here',
            r'manage.*subscription',
            r'update.*preferences',
            r'download.*app',
            r'get.*app',
            r'install.*app',
            r'follow us on',
            r'connect with us',
            r'social media',
            r'facebook.*twitter',
            r'instagram.*linkedin',
            r'terms.*conditions',
            r'privacy.*policy',
            r'legal.*notice',
            r'disclaimer',
            r'no longer receive',
            r'stop receiving',
            r'don\'t want to receive',
            r'if you received this',
            r'this email was sent',
            r'sent to.*because',
            r'you received this',
            r'view this email',
            r'display problems',
            r'email not displaying',
            r'view in browser',
            r'online version'
        ]
        
        # Common newsletter/notification domains
        self.filter_domains = [
            'mailchimp.com',
            'sendgrid.com',
            'constantcontact.com',
            'campaignmonitor.com',
            'mailgun.com',
            'postmarkapp.com',
            'convertkit.com',
            'aweber.com',
            'getresponse.com',
            'activecampaign.com',
            'hubspot.com',
            'salesforce.com',
            'marketo.com',
            'pardot.com',
            'customer.io',
            'braze.com',
            'leanplum.com',
            'airship.com',
            'onesignal.com',
            'pushwoosh.com'
        ]
        
        # Compile all regex patterns
        self.newsletter_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.newsletter_patterns]
        self.automated_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.automated_patterns]
        self.subject_filter_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.subject_filter_patterns]
        self.body_filter_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.body_filter_patterns]

    def should_filter_email(self, email: Dict) -> FilterResult:
        """
        Determine if an email should be filtered out (excluded from processing)
        
        Args:
            email: Dictionary containing email data with keys: From, To, Subject, body, etc.
            
        Returns:
            FilterResult with decision and reasoning
        """
        
        # Check sender email address
        sender_email = email.get('From', '').lower()
        for pattern in self.automated_regex:
            if pattern.search(sender_email):
                return FilterResult(
                    should_filter=True,
                    reason=f"Automated sender pattern: {pattern.pattern}",
                    confidence=0.9
                )
        
        # Check sender domain
        sender_domain = self._extract_domain(sender_email)
        if sender_domain in self.filter_domains:
            return FilterResult(
                should_filter=True,
                reason=f"Known email marketing domain: {sender_domain}",
                confidence=0.8
            )
        
        # Check subject line
        subject = email.get('Subject', '').lower()
        for pattern in self.subject_filter_regex:
            if pattern.search(subject):
                return FilterResult(
                    should_filter=True,
                    reason=f"Subject filter pattern: {pattern.pattern}",
                    confidence=0.7
                )
        
        # Check body content
        body = email.get('body', '').lower()
        for pattern in self.body_filter_regex:
            if pattern.search(body):
                return FilterResult(
                    should_filter=True,
                    reason=f"Body filter pattern: {pattern.pattern}",
                    confidence=0.6
                )
        
        # Check for very short or empty bodies (likely notifications)
        if len(body.strip()) < 50:
            return FilterResult(
                should_filter=True,
                reason="Very short or empty body content",
                confidence=0.5
            )
        
        # Check for high recipient count (likely newsletters/announcements)
        to_field = email.get('To', '').lower()
        cc_field = email.get('Cc', '').lower()
        bcc_field = email.get('Bcc', '').lower()
        
        all_recipients = f"{to_field} {cc_field} {bcc_field}"
        recipient_count = len([r.strip() for r in all_recipients.split(',') if r.strip() and '@' in r])
        
        if recipient_count > 10:
            return FilterResult(
                should_filter=True,
                reason=f"High recipient count: {recipient_count}",
                confidence=0.6
            )
        
        # Check for Gmail categories that indicate automated content
        label_ids = email.get('labelIds', [])
        if any(label in label_ids for label in ['CATEGORY_PROMOTIONS', 'CATEGORY_SOCIAL', 'CATEGORY_UPDATES']):
            return FilterResult(
                should_filter=True,
                reason=f"Gmail category indicates automated content: {label_ids}",
                confidence=0.7
            )
        
        # Check for common notification senders
        notification_senders = [
            'calendar-notification@google.com',
            'calendar-noreply@google.com',
            'drive-shares-noreply@google.com',
            'docs-noreply@google.com',
            'sheets-noreply@google.com',
            'slides-noreply@google.com',
            'meet-noreply@google.com',
            'classroom-noreply@google.com',
            'no-reply@accounts.google.com',
            'security-noreply@google.com',
            'password-assistance@accounts.google.com'
        ]
        
        if any(sender in notification_senders for sender in [sender_email]):
            return FilterResult(
                should_filter=True,
                reason=f"Known notification sender: {sender_email}",
                confidence=0.9
            )
        
        # If none of the filters matched, don't filter
        return FilterResult(
            should_filter=False,
            reason="No filtering criteria matched",
            confidence=0.0
        )
    
    def _extract_domain(self, email_address: str) -> str:
        """Extract domain from email address"""
        match = re.search(r'@([^>]+)', email_address)
        if match:
            return match.group(1).lower()
        return ""
    
    def filter_emails(self, emails: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter a list of emails into kept and filtered lists
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            Tuple of (kept_emails, filtered_emails)
        """
        kept_emails = []
        filtered_emails = []
        
        for email in emails:
            filter_result = self.should_filter_email(email)
            
            if filter_result.should_filter:
                email['_filter_reason'] = filter_result.reason
                email['_filter_confidence'] = filter_result.confidence
                filtered_emails.append(email)
            else:
                kept_emails.append(email)
        
        return kept_emails, filtered_emails

# Example usage
if __name__ == "__main__":
    # Test the filter with sample emails
    filter = EmailFilter()
    
    # Sample email that should be filtered
    newsletter_email = {
        'From': 'newsletter@company.com',
        'To': 'user@example.com',
        'Subject': '[Newsletter] Weekly Update - Click here to unsubscribe',
        'body': 'This is our weekly newsletter with updates and promotions. Click here to unsubscribe if you no longer wish to receive these emails.'
    }
    
    # Sample email that should be kept
    personal_email = {
        'From': 'colleague@company.com',
        'To': 'user@example.com',
        'Subject': 'Re: Project Discussion',
        'body': 'Hi, I wanted to follow up on our discussion about the project. Let me know when you have time to chat this week.'
    }
    
    # Test filtering
    newsletter_result = filter.should_filter_email(newsletter_email)
    personal_result = filter.should_filter_email(personal_email)
    
    print(f"Newsletter email filtered: {newsletter_result.should_filter} - {newsletter_result.reason}")
    print(f"Personal email filtered: {personal_result.should_filter} - {personal_result.reason}")