import re
import base64
from datetime import datetime
import config.settings as settings
from transformers import pipeline
import spacy

# Initialize the text classification pipeline
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_job_details(text):
    """Extract job-related details using spaCy NER"""
    doc = nlp(text)
    job_details = {
        'job_title': '',
        'company': '',
        'location': '',
        'deadline': ''
    }

    for ent in doc.ents:
        if ent.label_ == 'ORG':
            job_details['company'] = ent.text
        elif ent.label_ == 'GPE':
            job_details['location'] = ent.text
        elif ent.label_ == 'DATE':
            job_details['deadline'] = ent.text
        elif ent.label_ == 'JOB_TITLE':  # Custom label, you may need to train a custom model for this
            job_details['job_title'] = ent.text

    return job_details

def is_important_email(email_data):
    """Determine if an email is important using extracted job details"""
    subject = email_data.get('subject', '')
    sender = email_data.get('sender', '')
    body = email_data.get('body', '')

    job_details = extract_job_details(body)
    return any(job_details.values())  # Check if any job-related details are found

def extract_email_data(message):
    """Extract relevant data from an email message"""
    headers = message['payload']['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    body = ''
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                break
    return {
        'subject': subject,
        'sender': sender,
        'body': body
    }
