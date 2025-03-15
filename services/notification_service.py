import os
import requests
from datetime import datetime
from pathlib import Path
import logging
from transformers import pipeline
from utils.email_parser import extract_job_details

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the text generation pipeline
generator = pipeline("text-generation", model="gpt2")

class NotificationService:
    """Service for sending notifications to different platforms"""
    
    def __init__(self, config):
        self.config = config
        self.telegram_bot_token = config.get('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = config.get('TELEGRAM_CHAT_ID')
        self.whatsapp_enabled = config.get('WHATSAPP_ENABLED', False)
        self.whatsapp_phone = config.get('WHATSAPP_PHONE')

    def format_message(self, subject, body, sender, received_time):
        """Format the message using LLM"""
        job_details = extract_job_details(body)
        prompt = f"""
        Format the following email for a Telegram notification:
        Subject: {subject}
        Sender: {sender}
        Received Time: {received_time}
        Body: {body}
        Job Title: {job_details['job_title']}
        Company: {job_details['company']}
        Location: {job_details['location']}
        Deadline: {job_details['deadline']}
        """

        response = generator(prompt, max_length=150, num_return_sequences=1)
        formatted_message = response[0]['generated_text'].strip()
        return formatted_message
        
    def send_notification(self, subject, body, sender, received_time):
        """Send notification through all configured channels"""
        success = False
        formatted_message = self.format_message(subject, body, sender, received_time)
        
        # Try Telegram if configured
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                self.send_telegram_notification(formatted_message)
                success = True
            except Exception as e:
                logging.error(f"Failed to send Telegram notification: {str(e)}")
        else:
            logging.warning("Telegram notifications not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env file.")
        
        # Try WhatsApp if enabled and configured
        if self.whatsapp_enabled and self.whatsapp_phone:
            try:
                self.send_whatsapp_notification(formatted_message)
                success = True
            except Exception as e:
                logging.error(f"Failed to send WhatsApp notification: {str(e)}")
        
        return success

    def send_telegram_notification(self, message):
        """Send a notification via Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            'chat_id': self.telegram_chat_id,
            'text': message
        }
        response = requests.post(url, data=data)
        response.raise_for_status()

    def send_whatsapp_notification(self, message):
        """Send a notification via WhatsApp (placeholder)"""
        # Implement WhatsApp notification logic here
        pass