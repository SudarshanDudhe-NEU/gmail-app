import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Gmail API settings
GMAIL_USER_EMAIL = os.getenv('GMAIL_USER_EMAIL')
GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials/credentials.json')
GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'credentials/token.json')
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Email importance criteria
IMPORTANT_EMAIL_CRITERIA = {
    'important_senders': [
        r'noreply@linkedin\.com',
        r'jobs@indeed\.com',
        r'careers@company\.com',  # Add more known job application senders
        r'recruiter@company\.com'
    ],
    'important_subjects': [
        r'job application',
        r'interview',
        r'resume',
        r'CV',
        r'cover letter',
        r'position',
        r'opportunity',
        r'career',
        r'hiring',
        r'recruiter',
        r'HR',
        r'offer',
        r'application status'
    ],
    'important_keywords': [
        r'job application',
        r'interview',
        r'resume',
        r'CV',
        r'cover letter',
        r'position',
        r'opportunity',
        r'career',
        r'hiring',
        r'recruiter',
        r'HR',
        r'offer',
        r'application status'
    ]
}

# Additional important email keywords
IMPORTANT_EMAIL_KEYWORDS = [
    'job application',
    'interview',
    'resume',
    'CV',
    'cover letter',
    'position',
    'opportunity',
    'career',
    'hiring',
    'recruiter',
    'HR',
    'offer',
    'application status'
]

# Additional important email senders
IMPORTANT_EMAIL_SENDERS = [
    'noreply@linkedin.com',
    'jobs@indeed.com',
    'careers@company.com',  # Add more known job application senders
    'recruiter@company.com'
]

# Notification settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'False').lower() == 'true'
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE')

# Email processing settings
MAX_EMAILS_TO_CHECK = int(os.getenv('MAX_EMAILS_TO_CHECK', '1000'))
DAYS_TO_CHECK = int(os.getenv('DAYS_TO_CHECK', '7'))
IMPORTANCE_KEYWORDS = os.getenv('IMPORTANCE_KEYWORDS', 'urgent,important,interview,offer,job,application').split(',')
SENDER_ALLOWLIST = os.getenv('SENDER_ALLOWLIST', '').split(',') if os.getenv('SENDER_ALLOWLIST') else []

# Polling settings
CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', 300))  # Default: 5 minutes
MAX_RESULTS_PER_QUERY = int(os.getenv('MAX_RESULTS_PER_QUERY', 10))

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/gmail_monitor.log')