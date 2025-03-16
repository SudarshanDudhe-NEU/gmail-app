import logging
from datetime import datetime
from auth.gmail_auth import gmail_authenticate
from services.gmail_service import search_messages, get_message_details
from services.notification_service import NotificationService
from utils.email_parser import is_important_email, extract_email_data
import config.settings as settings
from utils.whatsapp_notifications import send_whatsapp_message

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

def check_old_emails(query, max_results=1000):
    logging.info("Starting manual check for old emails")
    service = gmail_authenticate()
    notification_service = NotificationService({
        'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
        'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
        'WHATSAPP_ENABLED': settings.WHATSAPP_ENABLED,
        'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
    })

    logging.info(f"Searching for emails with query: {query}")
    messages = []
    next_page_token = None

    while len(messages) < max_results:
        result = search_messages(service, query, next_page_token)
        if not result or 'messages' not in result:
            break
        messages.extend(result['messages'])
        next_page_token = result.get('nextPageToken')
        if not next_page_token:
            break

    if not messages:
        logging.info("No emails found")
    else:
        logging.info(f"Found {len(messages)} emails, checking importance...")
        important_emails = []
        for msg in messages[:max_results]:
            msg_details = get_message_details(service, msg['id'])
            email_data = extract_email_data(msg_details)
            if is_important_email(email_data):
                important_emails.append(email_data)
                logging.info(f"Important email found - ID: {msg['id']}")
                logging.info(f"Subject: {email_data['subject']}")
                logging.info(f"Sender: {email_data['sender']}")
                logging.info(f"Body: {email_data['body'][:100]}...")  # Print first 100 characters of the body

                # Send notifications
                notification_service.send_notification(
                    email_data['subject'],
                    email_data['body'],
                    email_data['sender'],
                    msg_details['internalDate']
                )

                # Send WhatsApp notification if enabled
                if settings.WHATSAPP_ENABLED:
                    send_whatsapp_message(settings.WHATSAPP_PHONE, f"Important email from {email_data['sender']}: {email_data['subject']}")
                    logging.info(f"WhatsApp notification sent for email {msg['id']}")

        logging.info(f"Found {len(important_emails)} important emails")

if __name__ == "__main__":
    # Customize your query here
    # Example: Search for emails from the last 7 days
    query = "newer_than:7d"
    check_old_emails(query, max_results=1000)