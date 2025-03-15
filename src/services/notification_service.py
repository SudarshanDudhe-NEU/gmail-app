import os
import requests
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications to different platforms"""
    
    def __init__(self, config):
        self.telegram_token = config.get('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = config.get('TELEGRAM_CHAT_ID')
        self.whatsapp_enabled = config.get('WHATSAPP_ENABLED', False)
        self.whatsapp_phone = config.get('WHATSAPP_PHONE')
        
    def send_telegram_notification(self, subject, sender, snippet, timestamp=None):
        """Send a notification to Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram notification skipped: missing configuration")
            return False
            
        try:
            # Format the message
            if timestamp:
                try:
                    dt_obj = datetime.fromtimestamp(int(timestamp) / 1000.0)
                    date_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date_str = "Unknown time"
            else:
                date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
            message = f"📬 *New Important Email*\n\n"
            message += f"*From:* {sender}\n"
            message += f"*Subject:* {subject}\n"
            message += f"*Time:* {date_str}\n\n"
            message += f"*Preview:*\n{snippet[:150]}..."
            
            # Send the telegram message
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Telegram notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return False
    
    def send_whatsapp_notification(self, subject, sender, snippet):
        """Send a notification via WhatsApp"""
        if not self.whatsapp_enabled or not self.whatsapp_phone:
            logger.warning("WhatsApp notification skipped: not enabled or missing phone number")
            return False
        
        try:
            # Note: This is a placeholder. Actual implementation would depend on the WhatsApp API service you're using
            # You might use pywhatkit, Twilio, or the WhatsApp Business API
            logger.info(f"Would send WhatsApp notification to {self.whatsapp_phone} (implementation needed)")
            
            # Example using pywhatkit (requires GUI and browser):
            # import pywhatkit
            # message = f"📬 New Important Email\nFrom: {sender}\nSubject: {subject}\n\n{snippet[:100]}..."
            # pywhatkit.sendwhatmsg_instantly(self.whatsapp_phone, message, wait_time=15)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp notification: {str(e)}")
            return False
            
    def notify_important_email(self, email_data):
        """Send notifications about an important email to configured channels"""
        subject = email_data.get('subject', 'No subject')
        sender = email_data.get('from', 'Unknown sender')
        snippet = email_data.get('snippet', 'No preview available')
        timestamp = email_data.get('timestamp')
        
        # Send to all configured notification channels
        telegram_result = self.send_telegram_notification(subject, sender, snippet, timestamp)
        whatsapp_result = False
        
        if self.whatsapp_enabled:
            whatsapp_result = self.send_whatsapp_notification(subject, sender, snippet)
            
        return {
            'telegram': telegram_result,
            'whatsapp': whatsapp_result
        }