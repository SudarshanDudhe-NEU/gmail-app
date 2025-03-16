#!/usr/bin/env python
# filepath: /Users/sudarshan/Job and Prep/Projects/gmail-app/test_notifications.py

import logging
import sys
import os
from datetime import datetime
import config.settings as settings
from services.notification_service import NotificationService
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

def test_telegram():
    """Test Telegram notifications"""
    logging.info("Testing Telegram notification...")
    
    notification_service = NotificationService({
        'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
        'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
        'WHATSAPP_ENABLED': False,
        'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
    })
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"Test Notification"
    body = f"This is a test notification sent at {current_time}"
    sender = "test@example.com"
    timestamp = str(int(datetime.now().timestamp() * 1000))
    
    try:
        result = notification_service.send_notification(subject, body, sender, timestamp)
        if result:
            logging.info("✅ Telegram notification sent successfully!")
        else:
            logging.error("❌ Failed to send Telegram notification")
    except Exception as e:
        logging.error(f"❌ Error sending Telegram notification: {e}")

def test_whatsapp():
    """Test WhatsApp notifications"""
    if not settings.WHATSAPP_ENABLED:
        logging.warning("WhatsApp notifications are disabled in settings. Skipping test.")
        return
    
    logging.info("Testing WhatsApp notification...")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Test WhatsApp notification sent at {current_time}"
    
    try:
        send_whatsapp_message(settings.WHATSAPP_PHONE, message)
        logging.info("✅ WhatsApp notification initiated!")
        logging.info("Note: WhatsApp Web should open in your browser. Please check if the message was sent.")
    except Exception as e:
        logging.error(f"❌ Error sending WhatsApp notification: {e}")

def main():
    """Run notification tests"""
    logging.info("Starting notification tests...")
    
    # Test Telegram
    test_telegram()
    
    # Test WhatsApp
    test_whatsapp()
    
    logging.info("Notification tests complete!")

if __name__ == "__main__":
    main()