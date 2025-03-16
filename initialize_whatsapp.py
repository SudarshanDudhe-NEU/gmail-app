#!/usr/bin/env python
# filepath: /Users/sudarshan/Job and Prep/Projects/gmail-app/initialize_whatsapp.py

import logging
import sys
import os
import shutil
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.whatsapp_notifications import (
    get_session_info,
    save_session_info,
    SESSION_INFO_FILE,
    CHROME_PROFILE_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def destroy_session():
    """Destroy the current WhatsApp session by deleting profile data"""
    try:
        # Delete the session info file
        if os.path.exists(SESSION_INFO_FILE):
            os.remove(SESSION_INFO_FILE)
            logger.info(f"Deleted session info file: {SESSION_INFO_FILE}")
        
        # Delete the Chrome profile directory
        if os.path.exists(CHROME_PROFILE_DIR):
            shutil.rmtree(CHROME_PROFILE_DIR)
            logger.info(f"Deleted Chrome profile directory: {CHROME_PROFILE_DIR}")
        
        logger.info("WhatsApp session successfully destroyed")
        return True
    except Exception as e:
        logger.error(f"Error destroying WhatsApp session: {str(e)}")
        return False

def check_session_status():
    """Check the current status of the WhatsApp session"""
    session_info = get_session_info()
    last_auth_date = session_info.get("last_auth_date")
    
    if not last_auth_date:
        logger.info("No active WhatsApp session found.")
        return False, None
    
    logger.info(f"WhatsApp session last authenticated on: {last_auth_date}")
    
    # Check if Chrome profile exists
    if not os.path.exists(CHROME_PROFILE_DIR):
        logger.warning("Chrome profile directory not found, session may be invalid.")
        return False, last_auth_date
        
    return True, last_auth_date

def init_session(force=False):
    """Initialize a new WhatsApp session"""
    logger.info("Starting WhatsApp Web initialization...")
    
    # Check if session is still valid and not forced reinitialization
    session_info = get_session_info()
    last_auth_date = session_info.get("last_auth_date")
    
    if not force and last_auth_date:
        logger.info("Session exists and force is not enabled. No need to reinitialize.")
        return True
    
    logger.info("Initializing WhatsApp Web session...")
    
    # Setup Chrome options - NOT headless for initial setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # Create chrome_profile directory if it doesn't exist
    os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_DIR}")
    
    # Add these to prevent crashes
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("detach", True)  # Keep the browser open
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com/")
        
        # Wait for user to scan QR code and for WhatsApp to load
        print("\n" + "="*50)
        print("Please scan the QR code in the browser window.")
        print("After scanning, wait until WhatsApp Web fully loads.")
        print("The browser will remain open until you confirm success.")
        print("="*50 + "\n")
        
        # Manual confirmation approach
        confirmation = input("\nHave you successfully scanned the QR code and seen your chats? (y/n): ")
        
        if confirmation.lower() == 'y':
            # Update session info with current date
            session_info = {"last_auth_date": datetime.datetime.now().isoformat()}
            save_session_info(session_info)
            
            logger.info("✅ WhatsApp Web has been successfully initialized!")
            logger.info("You can now close the browser window and run the Gmail monitor application.")
            return True
        else:
            logger.error("❌ WhatsApp Web initialization was not confirmed.")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing session: {str(e)}")
        return False

def interactive_menu():
    """Display an interactive menu for WhatsApp session management"""
    print("\n" + "="*50)
    print("WhatsApp Session Manager".center(50))
    print("="*50)
    
    has_session, last_auth = check_session_status()
    
    print("\nCurrent Status:")
    if has_session:
        print("✅ Active session found")
        print(f"📅 Last authenticated: {last_auth}")
    else:
        print("❌ No active session found")
    
    print("\nOptions:")
    print("1. Initialize a new session")
    print("2. Reinitialize existing session (force refresh)")
    print("3. Destroy current session and start fresh")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        init_session(force=False)
    elif choice == '2':
        init_session(force=True)
    elif choice == '3':
        confirm = input("Are you sure you want to destroy the current session? (y/n): ")
        if confirm.lower() == 'y':
            if destroy_session():
                time.sleep(1)  # Brief pause
                init_session(force=True)
        else:
            print("Operation cancelled.")
    elif choice == '4':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Import datetime here to avoid circular imports
    import datetime
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "destroy":
            destroy_session()
        elif arg == "status":
            check_session_status()
        elif arg == "init":
            init_session(force=False)
        elif arg == "force":
            init_session(force=True)
        else:
            print(f"Unknown argument: {arg}")
            print("Available commands: status, init, force, destroy")
    else:
        # No arguments, run interactive mode
        interactive_menu()