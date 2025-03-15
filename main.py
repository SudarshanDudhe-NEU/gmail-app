import time
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

from auth.gmail_auth import gmail_authenticate
from services.gmail_service import search_messages, get_message_details
from services.notification_service import NotificationService
from utils.email_parser import is_important_email, extract_email_data
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

class GmailMonitor:
    def __init__(self):
        self.service = None
        self.notification_service = NotificationService({
            'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
            'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
            'WHATSAPP_ENABLED': settings.WHATSAPP_ENABLED,
            'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
        })
        self.processed_ids = set()
        self.last_check_time = None
        self.load_processed_ids()

    def load_processed_ids(self):
        """Load processed email IDs from file"""
        id_file = Path('processed_emails.txt')
        try:
            if id_file.exists():
                with open(id_file, 'r') as f:
                    for line in f:
                        email_id = line.strip()
                        if email_id:
                            self.processed_ids.add(email_id)
                logging.info(f"Loaded {len(self.processed_ids)} processed email IDs")
        except Exception as e:
            logging.error(f"Error loading processed email IDs: {e}")

    def save_processed_id(self, email_id):
        """Save ID of a processed email"""
        try:
            with open('processed_emails.txt', 'a') as f:
                f.write(f"{email_id}\n")
            self.processed_ids.add(email_id)
        except Exception as e:
            logging.error(f"Error saving processed email ID: {e}")

    def authenticate(self):
        """Authenticate to Gmail API"""
        try:
            self.service = gmail_authenticate()
            logging.info("Authentication successful")
            return True
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
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
            logging.warning("Not authenticated, skipping email check")
            return
        
        # Record the current time as our check time
        current_check_time = datetime.now()
        
        # Build and execute search
        query = self.build_search_query()
        logging.info(f"Searching for emails with query: {query}")
        
        try:
            messages = search_messages(self.service, query)
            
            if not messages:
                logging.info("No new emails found")
                return
                
            logging.info(f"Found {len(messages)} new emails, checking importance...")
            
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
                if is_important_email(message_data):
                    important_count += 1
                    logging.info(f"Important email found - ID: {message_id}")
                    
                    # Extract and format email data
                    email_data = extract_email_data(message_data)
                    
                    # Send notifications
                    notification_results = self.notification_service.send_notification(
                        email_data['subject'],
                        email_data['body'],
                        email_data['sender'],
                        message_data['internalDate']
                    )
                    
                    if notification_results:
                        logging.info(f"Notifications sent for email {message_id}")
                    
                # Mark as processed
                self.save_processed_id(message_id)
            
            logging.info(f"Found {important_count} important emails")
            
        except Exception as e:
            logging.error(f"Error checking emails: {e}")
        finally:
            # Update the last check time
            self.last_check_time = current_check_time

    def run(self):
        """Run the email monitoring loop"""
        if not self.authenticate():
            logging.error("Failed to authenticate, exiting")
            return
            
        logging.info("Starting Gmail monitor")
        
        try:
            while True:
                self.check_for_new_emails()
                
                # Sleep until next check
                logging.info(f"Sleeping for {settings.CHECK_INTERVAL_SECONDS} seconds")
                time.sleep(settings.CHECK_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            logging.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            
        logging.info("Gmail monitor stopped")

if __name__ == "__main__":
    monitor = GmailMonitor()
    monitor.run()