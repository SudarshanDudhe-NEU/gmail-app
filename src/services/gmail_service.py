import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from pathlib import Path

def search_messages(service, query):
    """Search for messages that match the specified query"""
    try:
        result = service.users().messages().list(userId='me', q=query).execute()
        messages = result.get('messages', [])
        return messages
    except Exception as e:
        print(f"Error searching messages: {e}")
        return []

def get_message_details(service, message_id):
    """Get details of a specific message"""
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        return message
    except Exception as e:
        print(f"Error getting message details: {e}")
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
    
    with open(filename, 'rb') as fp:
        if main_type == 'text':
            msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        elif main_type == 'image':
            msg = MIMEImage(fp.read(), _subtype=sub_type)
        elif main_type == 'audio':
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
        else:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())

    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

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