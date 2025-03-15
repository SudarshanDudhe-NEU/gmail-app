import re
import base64
from datetime import datetime

def is_important_email(message_data, important_criteria):
    """
    Determine if an email is important based on configurable criteria
    
    Args:
        message_data: The message data from Gmail API
        important_criteria: Dict with rules to identify important emails
        
    Returns:
        bool: True if the email meets any importance criteria
    """
    # Get the headers and other message data
    headers = message_data.get('payload', {}).get('headers', [])
    header_dict = {header['name'].lower(): header['value'] for header in headers}
    
    # Extract key info
    sender = header_dict.get('from', '')
    subject = header_dict.get('subject', '')
    recipient = header_dict.get('to', '')
    cc = header_dict.get('cc', '')
    
    # Get labels and other metadata
    labels = message_data.get('labelIds', [])
    is_unread = 'UNREAD' in labels
    
    # Check for importance based on provided criteria
    if important_criteria.get('important_senders'):
        for sender_pattern in important_criteria['important_senders']:
            if re.search(sender_pattern, sender, re.IGNORECASE):
                return True
    
    if important_criteria.get('important_subjects'):
        for subject_pattern in important_criteria['important_subjects']:
            if re.search(subject_pattern, subject, re.IGNORECASE):
                return True
                
    if important_criteria.get('important_keywords'):
        snippet = message_data.get('snippet', '')
        for keyword in important_criteria['important_keywords']:
            if re.search(keyword, snippet, re.IGNORECASE) or re.search(keyword, subject, re.IGNORECASE):
                return True
    
    # Check for emails directed specifically to the user
    if important_criteria.get('direct_message', False):
        user_email = important_criteria.get('user_email', '')
        if user_email and user_email.lower() in recipient.lower() and ',' not in recipient:
            return True
    
    # Check for priority markers in the email
    if important_criteria.get('check_priority', False):
        if 'important' in labels or 'IMPORTANT' in labels:
            return True
            
    return False

def extract_email_data(message_data):
    """
    Extract key information from a Gmail message
    
    Returns:
        dict: Dictionary with key email data
    """
    payload = message_data.get('payload', {})
    headers = payload.get('headers', [])
    
    # Extract headers
    header_dict = {header['name'].lower(): header['value'] for header in headers}
    
    # Get timestamp
    timestamp = int(message_data.get('internalDate', 0))
    try:
        date_obj = datetime.fromtimestamp(timestamp / 1000.0)
        date_formatted = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except:
        date_formatted = "Unknown"
    
    # Get message body preview
    snippet = message_data.get('snippet', '')
    
    # Process body
    body = ''
    if 'body' in payload and 'data' in payload['body']:
        body_data = payload['body']['data']
        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
    
    # Alternatively, search through parts
    if not body and 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and 'body' in part and 'data' in part['body']:
                body_data = part['body']['data']
                body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                break
    
    # Get attachment info
    has_attachments = bool(message_data.get('payload', {}).get('parts', []))
    
    return {
        'id': message_data.get('id', ''),
        'thread_id': message_data.get('threadId', ''),
        'from': header_dict.get('from', ''),
        'to': header_dict.get('to', ''),
        'subject': header_dict.get('subject', 'No subject'),
        'date': date_formatted,
        'timestamp': timestamp,
        'snippet': snippet,
        'body': body,
        'labels': message_data.get('labelIds', []),
        'has_attachments': has_attachments
    }