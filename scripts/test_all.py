#!/usr/bin/env python

import os
import sys
import logging
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_whatsapp():
    print("\n🔍 Testing WhatsApp Session...")
    
    try:
        from utils.whatsapp_notifications import is_session_valid, send_whatsapp_message
        
        session_valid = is_session_valid()
        
        if session_valid:
            print("✅ WhatsApp session is valid")
            
            print("\n📱 Testing WhatsApp Messaging...")
            result = send_whatsapp_message(
                phone_number="917721976267",
                message="Test message from Gmail Monitor test suite",
                use_headless=True
            )
            
            if result:
                print("✅ WhatsApp message sent successfully")
                return True
            else:
                print("❌ Failed to send WhatsApp message")
                return False
        else:
            print("❌ WhatsApp session is not valid")
            print("   Run 'python scripts/initialize_whatsapp.py' to set up a session")
            return False
            
    except Exception as e:
        print(f"❌ Error testing WhatsApp: {e}")
        return False

def test_notifications():
    print("\n📧 Testing Notifications...")
    
    try:
        from services.notification_service import NotificationService
        import config.settings as settings
        
        notification_service = NotificationService({
            'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
            'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
            'WHATSAPP_ENABLED': settings.WHATSAPP_ENABLED,
            'WHATSAPP_PHONE': settings.WHATSAPP_PHONE
        })
        
        # Use the correct parameter name: received_time
        result = notification_service.send_notification(
            subject="Test Subject",
            body="Test body from test_all.py",
            sender="test@example.com",
            received_time=int(time.time() * 1000)
        )
        
        if result:
            print("✅ Notification sent successfully")
            return True
        else:
            print("❌ Failed to send notification")
            return False
            
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")
        return False

def test_email():
    print("\n📨 Testing Email Checking...")
    
    try:
        from auth.gmail_auth import gmail_authenticate
        from services.gmail_service import search_messages, get_message_details
        from utils.email_parser import extract_email_data, is_important_email
        import config.settings as settings
        
        # Authenticate
        service = gmail_authenticate()
        if not service:
            print("❌ Gmail authentication failed")
            return False
            
        print("✅ Gmail authentication successful")
        
        # Check for recent emails
        query = "newer_than:1d"
        print(f"Searching for emails with query: {query}")
        
        response = search_messages(service, query)
        if not response or 'messages' not in response:
            print("No emails found for testing")
            return True
            
        messages = response.get('messages', [])[:3]
        print(f"Found {len(messages)} emails for testing")
        
        for message in messages:
            message_id = message.get('id')
            message_data = get_message_details(service, message_id)
            
            if message_data:
                email_data = extract_email_data(message_data)
                print(f"Email: {email_data['subject']}")
                
                # Check importance
                is_important = is_important_email(email_data)
                print(f"  Important: {'Yes' if is_important else 'No'}")
                
        print("✅ Email checking test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing email checking: {e}")
        return False

def run_all_tests():
    print("\n==================================================")
    print("                  Test Suite                      ")
    print("==================================================")
    
    # Test WhatsApp
    whatsapp_ok = test_whatsapp()
    
    # Test notifications
    notifications_ok = test_notifications()
    
    # Test email
    email_ok = test_email()
    
    # Summary
    print("\n==================================================")
    print("                 Test Results                     ")
    print("==================================================")
    print(f"WhatsApp:      {'✅ PASS' if whatsapp_ok else '❌ FAIL'}")
    print(f"Notifications: {'✅ PASS' if notifications_ok else '❌ FAIL'}")
    print(f"Email:         {'✅ PASS' if email_ok else '❌ FAIL'}")
    print("==================================================")
    
    overall = all([whatsapp_ok, notifications_ok, email_ok])
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}")
    
    return overall

if __name__ == "__main__":
    run_all_tests()
