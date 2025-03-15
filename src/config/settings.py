import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Gmail API settings
GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')
GMAIL_USER_EMAIL = os.getenv('GMAIL_USER_EMAIL', '')

# Email importance criteria
IMPORTANT_EMAIL_CRITERIA = {
    'important_senders': [
        r'boss@company\.com',
        r'urgentnotifications@',
        r'alerts@',
        # Add more patterns as needed
    ],
    'important_subjects': [
        r'urgent',
        r'important',
        r'alert',
        r'action required',
        r'deadline',
        # Add more patterns as needed
    ],
    'important_keywords': [
        r'critical',
        r'immediate attention',
        r'asap',
        # Add more patterns as needed
    ],
    'direct_message': True,
    'check_priority': True,
    'user_email': GMAIL_USER_EMAIL
}

# Notification settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'False').lower() == 'true'
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE', '')

# Polling settings
CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', 300))  # Default: 5 minutes
MAX_RESULTS_PER_QUERY = int(os.getenv('MAX_RESULTS_PER_QUERY', 10))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'gmail_monitor.log')