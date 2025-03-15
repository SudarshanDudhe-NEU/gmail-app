import time
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.auth.gmail_auth import gmail_authenticate
from src.services.gmail_service import search_messages, get_message_details
from src.services.notification_service import NotificationService
from src.utils.email_parser import is_important_email, extract_email_data
import config.settings as settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GmailMonitor:
    def __init__(self):
        self.service = None
        self.last_check_time = None
        self.notification_service = NotificationService({
            'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
            'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
            'WHATSAPP_ENABLED': settings.WHATSAPP_ENABLED,
            'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
        })
        self.processed_ids = set()
        self.load_processed_ids()
        
    def load_processed_ids(self):
        """Load IDs of already processed emails"""
        try:
            id_file = Path('processed_emails.txt')
            if id_file.exists():
                with open(id_file, 'r') as f:
                    for line in f:
                        email_id = line.strip()
                        if email_id:
                            self.processed_ids.add(email_id)
                logger.info(f"Loaded {len(self.processed_ids)} processed email IDs")
        except Exception as e:
            logger.error(f"Error loading processed email IDs: {e}")
    
    def save_processed_id(self, email_id):
        """Save ID of a processed email"""
        try:
            with open('processed_emails.txt', 'a') as f:
                f.write(f"{email_id}\n")
            self.processed_ids.add(email_id)
        except Exception as e:
            logger.error(f"Error saving processed email ID: {e}")
    
    def authenticate(self):
        """Authenticate to Gmail API"""
        try:
            self.service = gmail_authenticate()
            logger.info("Authentication successful")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def build_search_query(self):
        """Build Gmail search query based on time"""
        query = ""
        
        # Add time constraint if we have a last check time
        if self.last_check_time:
            # Convert to Gmail's search format
            after_date = self.last_check_time.strftime("%Y/%m/%d")
            query += f"after:{after_date} "
        else:
            # Default to last 24 hours if no previous check time
            query += "newer_than:1d "
        
        # Only get unread emails
        query += "is:unread"
        
        return query
    
    def check_for_new_emails(self):
        """Check for new important emails"""
        if not self.service:
            logger.warning("Not authenticated, skipping email check")
            return
        
        # Record the current time as our check time
        current_check_time = datetime.now()
        
        # Build and execute search
        query = self.build_search_query()
        logger.info(f"Searching for emails with query: {query}")
        
        try:
            messages = search_messages(self.service, query)
            
            if not messages:
                logger.info("No new emails found")
                return
                
            logger.info(f"Found {len(messages)} new emails, checking importance...")
            
            important_count = 0
            
            for message in messages[:settings.MAX_RESULTS_PER_QUERY]:
                message_id = message.get('id')
                
                # Skip if we've already processed this email
                if message_id in self.processed_ids:
                    continue
                    
                # Get full message details
                message_data = get_message_details(self.service, message_id)
                
                if not message_data:
                    continue
                
                # Check if this email is important
                if is_important_email(message_data, settings.IMPORTANT_EMAIL_CRITERIA):
                    important_count += 1
                    logger.info(f"Important email found - ID: {message_id}")
                    
                    # Extract and format email data
                    email_data = extract_email_data(message_data)
                    
                    # Send notifications
                    notification_results = self.notification_service.notify_important_email(email_data)
                    
                    if notification_results['telegram'] or notification_results['whatsapp']:
                        logger.info(f"Notifications sent for email {message_id}")
                    
                # Mark as processed
                self.save_processed_id(message_id)
            
            logger.info(f"Found {important_count} important emails")
            
        except Exception as e:
            logger.error(f"Error checking emails: {e}")
        finally:
            # Update the last check time
            self.last_check_time = current_check_time
    
    def run(self):
        """Run the email monitoring loop"""
        if not self.authenticate():
            logger.error("Failed to authenticate, exiting")
            return
            
        logger.info("Starting Gmail monitor")
        
        try:
            while True:
                self.check_for_new_emails()
                
                # Sleep until next check
                logger.info(f"Sleeping for {settings.CHECK_INTERVAL_SECONDS} seconds")
                time.sleep(settings.CHECK_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        logger.info("Gmail monitor stopped")


if __name__ == "__main__":
    monitor = GmailMonitor()
    monitor.run()