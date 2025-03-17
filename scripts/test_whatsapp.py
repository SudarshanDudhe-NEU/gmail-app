#!/usr/bin/env python

# Import helper to set up path for imports
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))

import logging
import time
from datetime import datetime
import config.settings as settings
from utils.whatsapp_notifications import (
    send_whatsapp_message,
    is_session_valid,
    check_and_reinitialize_session,
    get_session_info
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_session_validity():
    """Test if the WhatsApp session is valid"""
    logger.info("Testing WhatsApp session validity...")
    
    session_info = get_session_info()
    last_auth = session_info.get("last_auth_date")
    
    if last_auth:
        logger.info(f"Session info found. Last authentication: {last_auth}")
    else:
        logger.warning("No session information found.")
    
    is_valid = is_session_valid()
    if is_valid:
        logger.info("✅ WhatsApp session is valid")
    else:
        logger.warning("❌ WhatsApp session is invalid or expired")
    
    return is_valid

def test_headless_message():
    """Test sending a WhatsApp message in headless mode"""
    if not settings.WHATSAPP_ENABLED:
        logger.warning("WhatsApp notifications are disabled in settings. Skipping test.")
        return False
    
    logger.info("Testing WhatsApp message sending in headless mode...")
    
    if not is_session_valid():
        logger.warning("Session is not valid. Headless mode may fail.")
        if not check_and_reinitialize_session():
            logger.error("Failed to reinitialize session. Try running initialize_whatsapp.py first.")
            return False
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Test WhatsApp notification (headless mode) sent at {current_time}"
    
    try:
        result = send_whatsapp_message(
            phone_number=settings.WHATSAPP_PHONE,
            message=message,
            use_headless=True
        )
        
        if result:
            logger.info("✅ WhatsApp message sent successfully in headless mode!")
        else:
            logger.error("❌ Failed to send WhatsApp message in headless mode")
        
        return result
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message in headless mode: {e}")
        return False

def test_visible_message():
    """Test sending a WhatsApp message in visible mode"""
    if not settings.WHATSAPP_ENABLED:
        logger.warning("WhatsApp notifications are disabled in settings. Skipping test.")
        return False
    
    logger.info("Testing WhatsApp message sending in visible mode...")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Test WhatsApp notification (visible browser mode) sent at {current_time}"
    
    try:
        result = send_whatsapp_message(
            phone_number=settings.WHATSAPP_PHONE,
            message=message,
            use_headless=False
        )
        
        if result:
            logger.info("✅ WhatsApp message sent successfully in visible mode!")
        else:
            logger.error("❌ Failed to send WhatsApp message in visible mode")
        
        return result
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message in visible mode: {e}")
        return False

def interactive_menu():
    """Display an interactive test menu"""
    print("\n" + "="*50)
    print("WhatsApp Testing Menu".center(50))
    print("="*50 + "\n")
    
    session_valid = test_session_validity()
    
    print("\nOptions:")
    print("1. Test sending message in headless mode")
    print("2. Test sending message in visible browser mode")
    print("3. Run all tests")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        test_headless_message()
    elif choice == '2':
        test_visible_message()
    elif choice == '3':
        test_headless_message()
        time.sleep(3)  # Brief pause between tests
        test_visible_message()
    elif choice == '4':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "check":
            test_session_validity()
        elif arg == "headless":
            test_headless_message()
        elif arg == "visible":
            test_visible_message()
        elif arg == "all":
            test_session_validity()
            test_headless_message()
            test_visible_message()
        else:
            print(f"Unknown argument: {arg}")
            print("Available commands: check, headless, visible, all")
    else:
        # No arguments, run interactive mode
        interactive_menu()