import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from pathlib import Path
from googleapiclient.discovery import build
import config.settings as settings
from base64 import urlsafe_b64encode

def search_messages(service, query, page_token=None):
    try:
        response = service.users().messages().list(
            userId='me',
            q=query,
            pageToken=page_token,
            maxResults=100  # Adjust as needed, Gmail API allows up to 500
        ).execute()
        return response
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def get_message_details(service, msg_id):
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def parse_message_headers(headers):
    """Extract key information from message headers"""
    message_info = {
        'from': '',
        'to': '',
        'subject': '',
        'date': ''
    }
    
    for header in headers:
        name = header.get('name', '').lower()
        if name in message_info:
            message_info[name] = header.get('value', '')
    
    return message_info

def extract_text_content(part_data):
    """Extract and decode text content from a message part"""
    if not part_data:
        return ""
    
    decoded_bytes = base64.urlsafe_b64decode(part_data)
    return decoded_bytes.decode('utf-8', errors='replace')

def parse_parts(service, parts, message_id):
    """Parse message parts to extract content and attachments"""
    content = {
        'plain': '',
        'html': '',
        'attachments': []
    }
    
    if not parts:
        return content
    
    for part in parts:
        mime_type = part.get('mimeType', '')
        body = part.get('body', {})
        part_data = body.get('data')
        
        # Handle nested parts
        if part.get('parts'):
            nested_content = parse_parts(service, part.get('parts'), message_id)
            for key, value in nested_content.items():
                if isinstance(value, list):
                    content[key].extend(value)
                elif value:
                    if not content[key]:
                        content[key] = value
                    else:
                        content[key] += value
        
        # Handle text content
        elif mime_type == 'text/plain' and part_data:
            content['plain'] += extract_text_content(part_data)
        
        elif mime_type == 'text/html' and part_data:
            content['html'] += extract_text_content(part_data)
        
        # Handle attachments
        elif body.get('attachmentId'):
            filename = part.get('filename', 'attachment')
            attachment = {
                'id': body.get('attachmentId'),
                'filename': filename,
                'mime_type': mime_type,
                'size': body.get('size', 0)
            }
            content['attachments'].append(attachment)
    
    return content

def download_attachment(service, message_id, attachment_id, output_dir=None):
    """Download an attachment from a message"""
    try:
        attachment = service.users().messages().attachments().get(
            userId='me', messageId=message_id, id=attachment_id
        ).execute()
        
        data = attachment.get('data')
        if not data:
            return None
        
        file_data = base64.urlsafe_b64decode(data)
        
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            return file_path
        else:
            return file_data
            
    except Exception as e:
        print(f"Error downloading attachment: {e}")
        return None

def add_attachment(message, filename):
    """Add an attachment to an email message"""
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    
    if main_type == 'text':
        with open(filename, 'rb') as fp:
            msg = MIMEText(fp.read().decode(), _subtype=sub_type)
    elif main_type == 'image':
        with open(filename, 'rb') as fp:
            msg = MIMEImage(fp.read(), _subtype=sub_type)
    elif main_type == 'audio':
        with open(filename, 'rb') as fp:
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
    else:
        with open(filename, 'rb') as fp:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
    
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

def build_message(destination, subject, body, attachments=None):
    """Build an email message"""
    if attachments is None:
        attachments = []
    
    sender_email = settings.GMAIL_USER_EMAIL
    
    if not attachments:  # no attachments given
        message = MIMEText(body)
        message['to'] = destination
        message['from'] = sender_email
        message['subject'] = subject
    else:
        message = MIMEMultipart()
        message['to'] = destination
        message['from'] = sender_email
        message['subject'] = subject
        message.attach(MIMEText(body))
        for filename in attachments:
            add_attachment(message, filename)
    
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, destination, subject, body, attachments=None):
    """Send an email message"""
    try:
        message = build_message(destination, subject, body, attachments)
        sent_message = service.users().messages().send(
            userId="me",
            body=message
        ).execute()
        return sent_message
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return None

def batch_modify_emails(service, query, add_labels=None, remove_labels=None):
    """Batch modify emails with specified labels"""
    if add_labels is None:
        add_labels = []
    if remove_labels is None:
        remove_labels = []
        
    messages = search_messages(service, query)
    if not messages:
        return None
        
    return service.users().messages().batchModify(
        userId='me',
        body={
            'ids': [msg['id'] for msg in messages],
            'addLabelIds': add_labels,
            'removeLabelIds': remove_labels
        }
    ).execute()

def mark_as_read(service, query):
    """Mark emails matching the query as read"""
    return batch_modify_emails(service, query, remove_labels=['UNREAD'])

def mark_as_unread(service, query):
    """Mark emails matching the query as unread"""
    return batch_modify_emails(service, query, add_labels=['UNREAD'])

def delete_messages(service, query, batch_size=1000):
    """Delete messages matching the query"""
    messages = search_messages(service, query)
    if not messages:
        return None
        
    # Process in batches to avoid API limits
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i+batch_size]
        service.users().messages().batchDelete(
            userId='me',
            body={
                'ids': [msg['id'] for msg in batch]
            }
        ).execute()
    
    return True

def build_message(destination, subject, body, sender, attachments=None):
    """Build an email message with optional attachments"""
    if not attachments:
        message = MIMEText(body)
    else:
        message = MIMEMultipart()
        message.attach(MIMEText(body))
        for filename in attachments:
            add_attachment(message, filename)

    message['to'] = destination
    message['from'] = sender
    message['subject'] = subject
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, destination, subject, body, sender=None, attachments=None):
    """Send an email message via Gmail API"""
    try:
        if not sender:
            # Get user's email address
            profile = service.users().getProfile(userId='me').execute()
            sender = profile.get('emailAddress', '')
        
        message = build_message(destination, subject, body, sender, attachments)
        sent_message = service.users().messages().send(
            userId="me",
            body=message
        ).execute()
        
        return sent_message
    except Exception as e:
        print(f"Error sending message: {e}")
        return None