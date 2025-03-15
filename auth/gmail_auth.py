import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import logging

# If modifying these scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_authenticate():
    """Authenticate to Gmail API using OAuth 2.0"""
    creds = None
    
    # Get credential file path from environment or use default
    credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')
    
    # Load token from file if it exists
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            # Use a specific port that matches one of your registered redirect URIs
            creds = flow.run_local_server(port=8080)
            
        # Save credentials for next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return Gmail API service
    return build('gmail', 'v1', credentials=creds)