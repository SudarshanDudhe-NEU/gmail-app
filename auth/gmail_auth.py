import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path

# Define the authentication scope
SCOPES = ['https://mail.google.com/']

def gmail_authenticate():
    """Authenticate to Gmail API using OAuth 2.0"""
    creds = None
    token_path = Path("token.pickle")
    
    # Load credentials from token file if it exists
    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    
    # Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    
    # Build and return the Gmail API service
    return build('gmail', 'v1', credentials=creds)