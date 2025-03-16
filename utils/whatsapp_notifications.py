import time
import urllib.parse
import os
import json
import datetime
import logging
import pywhatkit as pwk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logger = logging.getLogger(__name__)

# Constants
SESSION_INFO_FILE = "whatsapp_session_info.json"
SESSION_EXPIRY_DAYS = 14  # WhatsApp sessions typically last around 14 days
CHROME_PROFILE_DIR = "./chrome_profile"

def get_session_info():
    """Get WhatsApp session information from the JSON file"""
    if os.path.exists(SESSION_INFO_FILE):
        try:
            with open(SESSION_INFO_FILE, 'r') as file:
                return json.load(file)
        except:
            return {"last_auth_date": None}
    return {"last_auth_date": None}

def save_session_info(session_info):
    """Save WhatsApp session information to the JSON file"""
    with open(SESSION_INFO_FILE, 'w') as file:
        json.dump(session_info, file)

def is_session_valid():
    """Check if the WhatsApp session is still valid"""
    session_info = get_session_info()
    last_auth_date = session_info.get("last_auth_date")
    
    if not last_auth_date:
        return False
    
    # Convert string date to datetime object
    last_auth = datetime.datetime.fromisoformat(last_auth_date)
    
    # Check if session is expired (older than SESSION_EXPIRY_DAYS)
    current_date = datetime.datetime.now()
    delta = current_date - last_auth
    
    return delta.days < SESSION_EXPIRY_DAYS

def initialize_whatsapp_session(force=False):
    """
    Initialize WhatsApp Web session with visible browser to scan QR code
    
    Args:
        force: If True, forces reinitialization even if session seems valid
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    # Check if session is still valid and not forced reinitialization
    if not force and is_session_valid():
        logger.info("Session is still valid. No need to reinitialize.")
        return True
    
    logger.info("Initializing WhatsApp Web session...")
    
    # Setup Chrome options - NOT headless for initial setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_DIR}")
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com/")
        
        # Wait for user to scan QR code and for WhatsApp to load
        logger.info("\n" + "="*50)
        logger.info("Please scan the QR code in the browser window that opened.")
        logger.info("After scanning, wait until WhatsApp Web fully loads.")
        logger.info("="*50 + "\n")
        
        # Wait for user avatar to appear indicating successful login
        try:
            # Increased timeout to 120 seconds
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='menu-bar-user-avatar']"))
            )
            logger.info("QR code successfully scanned and WhatsApp Web loaded!")
            
            # Update session info with current date
            session_info = {"last_auth_date": datetime.datetime.now().isoformat()}
            save_session_info(session_info)
            
            logger.info("Session initialized successfully.")
            logger.info("You can now close this browser.")
            
            # Wait a bit before closing
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Could not confirm WhatsApp Web loaded: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Error initializing session: {str(e)}")
        return False
    
    finally:
        # Close the browser
        driver.quit()

def check_and_reinitialize_session():
    """Check if session needs reinitialization and do it if necessary"""
    if not is_session_valid():
        logger.info("WhatsApp session has expired or doesn't exist.")
        return initialize_whatsapp_session()
    return True

def send_whatsapp_message_headless(phone_number, message):
    """
    Send WhatsApp message using a headless browser with saved session
    
    Args:
        phone_number: Phone number with country code but without + or spaces
        message: Message to send
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    # Check and reinitialize session if needed
    if not check_and_reinitialize_session():
        logger.error("Failed to initialize or verify session. Message not sent.")
        return False
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # New headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_DIR}")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Strip the "+" if present
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # URL encode the message
        encoded_message = urllib.parse.quote(message)
        
        # Create the WhatsApp URL with the phone number and message
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        
        # Open the URL
        driver.get(url)
        
        logger.info(f"Sending message to {phone_number}...")
        
        # Wait for the message input box to load
        input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )
        
        # Wait for send button to be clickable
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send']"))
        )
        
        # Click the send button
        send_button.click()
        
        # Wait a moment for the message to be sent
        time.sleep(2)
        
        logger.info(f"Message sent to {phone_number} successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        # Take screenshot for debugging
        driver.save_screenshot('error_screenshot.png')
        # If we get authentication error, let's invalidate the session
        if "auth" in str(e).lower() or "login" in str(e).lower():
            logger.warning("Authentication issue detected. Session might be expired.")
            # Force session reinitialization next time
            session_info = {"last_auth_date": None}
            save_session_info(session_info)
        return False
    
    finally:
        # Close the browser
        driver.quit()

def send_whatsapp_message_pywhatkit(phone_number, message):
    """
    Send WhatsApp message using pywhatkit (visible browser)
    
    Args:
        phone_number: Phone number with country code in format "+XXXXXXXXXXXX"
        message: Message to send
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        # Check if our session tracking thinks the session is valid
        if not is_session_valid():
            logger.info("Session may be expired. PyWhatKit will open a new browser window.")
        
        # Send message immediately using pywhatkit
        logger.info(f"Sending message to {phone_number} using PyWhatKit...")
        pwk.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=message,
            tab_close=True,  # Close browser tab after sending
            wait_time=20     # Increased wait time to allow for page loading
        )
        
        # Update session info after successful sending
        session_info = {"last_auth_date": datetime.datetime.now().isoformat()}
        save_session_info(session_info)
        logger.info(f"Message sent to {phone_number} successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error sending message using PyWhatKit: {str(e)}")
        return False

def send_whatsapp_message(phone_number, message, use_headless=True):
    """
    Send WhatsApp message using the appropriate method based on use_headless flag
    
    Args:
        phone_number: Phone number with country code in format "+XXXXXXXXXXXX"
        message: Message to send
        use_headless: Whether to use headless browser (True) or visible browser (False)
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    if use_headless:
        # Remove "+" if present for the headless version
        clean_number = phone_number[1:] if phone_number.startswith("+") else phone_number
        return send_whatsapp_message_headless(clean_number, message)
    else:
        return send_whatsapp_message_pywhatkit(phone_number, message)