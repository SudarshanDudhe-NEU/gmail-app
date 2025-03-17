#!/usr/bin/env python

# Import helper to set up path for imports
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))

import logging
import datetime
import config.settings as settings
from services.notification_service import NotificationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_notifications():
    """Test notification service functionality"""
    logger.info("Testing notification service...")
    
    notification_service = NotificationService({
        'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
        'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
        'WHATSAPP_ENABLED': settings.WHATSAPP_ENABLED,
        'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
    })
    
    # Test email data
    subject = "Test Notification"
    body = "This is a test notification from Gmail Monitor app."
    sender = "test@example.com"
    # The parameter should be received_time, not timestamp
    import time
    received_time = int(time.time() * 1000)  # Current time in milliseconds
    
    # Send test notification with the correct parameter name
    result = notification_service.send_notification(
        subject=subject,
        body=body,
        sender=sender,
        received_time=received_time  # Use received_time instead of timestamp
    )
    
    if result:
        logger.info("✅ Notification test successful!")
    else:
        logger.error("❌ Notification test failed!")
    
    return result

if __name__ == "__main__":
    print("\n==================================================")
    print("           Notification Service Test              ")
    print("==================================================\n")
    
    result = test_notifications()
    
    if result:
        print("\n✅ Notification test completed successfully!")
    else:
        print("\n❌ Notification test failed. Check logs for details.")