#!/usr/bin/env python

# Import helper to set up path for imports
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))

import logging
from datetime import datetime, timedelta
import config.settings as settings
from auth.gmail_auth import gmail_authenticate
from services.gmail_service import search_messages, get_message_details
from utils.email_parser import is_important_email, extract_email_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_email_check():
    """Test email checking functionality"""
    logger.info("Testing email checking functionality...")
    
    # Authenticate
    try:
        service = gmail_authenticate()
        if not service:
            logger.error("❌ Authentication failed")
            return False
        
        logger.info("✅ Authentication successful")
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return False
    
    # Search for a few recent emails
    try:
        # Get emails from last day
        query = "newer_than:1d"
        logger.info(f"Searching for emails with query: {query}")
        
        response = search_messages(service, query)
        if not response or 'messages' not in response:
            logger.warning("No emails found for testing")
            return True  # Not a failure, just no emails
        
        messages = response.get('messages', [])
        
        # Limit to first 3 for testing
        messages = messages[:3]
        
        logger.info(f"Found {len(messages)} emails for testing")
        
        # Process emails
        for message in messages:
            message_id = message.get('id')
            message_data = get_message_details(service, message_id)
            
            if not message_data:
                logger.warning(f"Could not get details for message {message_id}")
                continue
            
            email_data = extract_email_data(message_data)
            
            logger.info(f"Testing email: {email_data['subject']} from {email_data['sender']}")
            
            # Check importance
            is_important = is_important_email(email_data)
            
            if is_important:
                logger.info(f"✅ Email marked as important: {email_data['subject']}")
            else:
                logger.info(f"❌ Email not marked as important: {email_data['subject']}")
        
        logger.info("Email check test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during email check test: {e}")
        return False

if __name__ == "__main__":
    print("\n==================================================")
    print("           Email Checking Test                    ")
    print("==================================================\n")
    
    result = test_email_check()
    
    if result:
        print("\n✅ Email checking test completed successfully!")
    else:
        print("\n❌ Email checking test failed. Check logs for details.")