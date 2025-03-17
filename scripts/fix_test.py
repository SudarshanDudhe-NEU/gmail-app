#!/usr/bin/env python

import os
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_settings():
    """Check configuration settings"""
    import config.settings as settings
    
    print("\nChecking settings:")
    print(f"- IMPORTANCE_KEYWORDS (type): {type(settings.IMPORTANCE_KEYWORDS)}")
    if hasattr(settings, 'IMPORTANCE_KEYWORDS'):
        print(f"- IMPORTANCE_KEYWORDS (value): {settings.IMPORTANCE_KEYWORDS}")
    else:
        print("- IMPORTANCE_KEYWORDS not defined!")
    
    # Check WhatsApp settings
    print(f"- WHATSAPP_ENABLED: {settings.WHATSAPP_ENABLED}")
    print(f"- WHATSAPP_PHONE: {settings.WHATSAPP_PHONE}")

def test_whatsapp_simple():
    """Simple WhatsApp test"""
    from utils.whatsapp_notifications import send_whatsapp_message, is_session_valid
    
    print("\nTesting WhatsApp:")
    if is_session_valid():
        print("- Session is valid")
        
        # Check function signature
        import inspect
        sig = inspect.signature(send_whatsapp_message)
        print(f"- Function parameters: {list(sig.parameters.keys())}")
        
        # Try to send a message
        try:
            # Use the parameter names from the signature
            params = {}
            if 'target_number' in sig.parameters:
                params['target_number'] = "917721976267"
            elif 'phone' in sig.parameters:
                params['phone'] = "917721976267"
                
            if 'message' in sig.parameters:
                params['message'] = "Test message from fix script"
                
            print(f"- Calling with parameters: {params}")
            result = send_whatsapp_message(**params)
            
            if result:
                print("- Message sent successfully!")
            else:
                print("- Failed to send message")
        except Exception as e:
            print(f"- Error sending message: {e}")
    else:
        print("- Session is not valid")

def test_notification_simple():
    """Simple notification test"""
    from services.notification_service import NotificationService
    import config.settings as settings
    
    print("\nTesting NotificationService:")
    
    # Create service
    notification_service = NotificationService({
        'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
        'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
        'WHATSAPP_ENABLED': settings.WHATSAPP_ENABLED,
        'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
    })
    
    # Check function signature
    import inspect
    sig = inspect.signature(notification_service.send_notification)
    print(f"- Function parameters: {list(sig.parameters.keys())}")
    
    # Try to send a notification
    try:
        params = {
            'subject': 'Test Subject',
            'body': 'Test body',
            'sender': 'test@example.com'
        }
        
        # Add timestamp if it's a parameter
        if 'timestamp' in sig.parameters:
            import time
            params['timestamp'] = int(time.time() * 1000)
            
        print(f"- Calling with parameters: {params}")
        result = notification_service.send_notification(**params)
        
        if result:
            print("- Notification sent successfully!")
        else:
            print("- Failed to send notification")
    except Exception as e:
        print(f"- Error sending notification: {e}")
        
if __name__ == "__main__":
    print("\n==================================================")
    print("               Fix Test Script                    ")
    print("==================================================")
    
    check_settings()
    test_whatsapp_simple()
    test_notification_simple()
    
    print("\n==================================================")
    print("                  Done                            ")
    print("==================================================")