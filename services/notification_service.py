import os
import requests
from datetime import datetime
from pathlib import Path
import logging
from utils.email_parser import extract_job_title, extract_company, extract_location, extract_salary
from utils.whatsapp_notifications import send_whatsapp_message, is_session_valid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Llama 3.2 integration
def generate_summary_with_llama(content, max_length=150):
    """Generate a summary of email content using Llama 3.2"""
    try:
        prompt = f"""
        Summarize the following email content in a concise way (max 2-3 sentences):

        {content[:1000]}
        """
        
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            summary = result["response"].strip()
            return summary[:max_length] + ("..." if len(summary) > max_length else "")
        else:
            logger.error(f"Error calling Llama API: {response.status_code}")
            return content[:max_length] + "..."
    except Exception as e:
        logger.error(f"Exception in generate_summary_with_llama: {str(e)}")
        return content[:max_length] + "..."

class NotificationService:
    """Service for sending notifications to different platforms"""
    
    def __init__(self, config):
        self.config = config
        self.telegram_bot_token = config.get('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = config.get('TELEGRAM_CHAT_ID')
        self.whatsapp_enabled = config.get('WHATSAPP_ENABLED', False)
        self.whatsapp_phone = config.get('WHATSAPP_PHONE')
        self.use_llama = config.get('USE_LLAMA', True)  # Add config option for Llama
        self.logger = logger

    def format_message(self, subject, body, sender, received_time):
        """Format message for notifications with relevant details and stylish formatting"""
        try:
            # Get timestamp - handle both string and int types
            try:
                if isinstance(received_time, str):
                    # Try to convert string to int if it's numeric
                    if received_time.isdigit():
                        received_time = int(received_time)
                    else:
                        # If it's not numeric, use current time
                        received_time = int(datetime.now().timestamp() * 1000)
                
                # Now proceed with timestamp conversion
                received_dt = datetime.fromtimestamp(received_time / 1000)
                time_str = received_dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                # Fallback to current time if conversion fails
                time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            # Extract job details if available
            job_title = extract_job_title(body) if body else None
            company = extract_company(body) if body else None
            location = extract_location(body) if body else None
            salary = extract_salary(body) if body else None
            
            # Build message with stylish formatting
            message = f"📨 *Important Email Alert*\n\n"
            message += f"*Subject:* _{subject}_\n"  # Subject in italic
            message += f"*From:* _{sender}_\n"      # Sender in italic
            message += f"*Time:* _{time_str}_\n\n"  # Time in italic
            
            # Add job details with monospace formatting for values
            if job_title:
                message += f"*Position:* `{job_title}`\n"
            if company:
                message += f"*Company:* `{company}`\n"
            if location:
                message += f"*Location:* `{location}`\n"
            if salary:
                message += f"*Salary:* `{salary}`\n"
            
            # Add excerpt of body with intelligent summary if Llama is enabled
            if body:
                message += f"\n*Summary:* "
                if self.use_llama:
                    try:
                        summary = generate_summary_with_llama(body)
                        message += f"_{summary}_\n"
                    except Exception as e:
                        # Fallback to simple preview if Llama fails
                        preview = body[:150].replace('\n', ' ').strip()
                        message += f"_{preview}..._\n"
                        logger.error(f"Failed to generate Llama summary: {e}")
                else:
                    # Use simple preview without Llama
                    preview = body[:150].replace('\n', ' ').strip()
                    message += f"_{preview}..._\n"
            
            return message
        except Exception as e:
            logger.error(f"Error formatting message: {e}")
            return f"New email from {sender}: {subject}"

    def send_notification(self, subject, body, sender, received_time):
        """Send notification through all configured channels"""
        success = False
        formatted_message = self.format_message(subject, body, sender, received_time)
        
        # Try Telegram if configured
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                self.send_telegram_notification(formatted_message)
                success = True
                logger.info("Telegram notification sent successfully")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {str(e)}")
        else:
            logger.warning("Telegram notifications not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env file.")
        
        # Try WhatsApp if enabled and configured
        if self.whatsapp_enabled and self.whatsapp_phone:
            try:
                self.send_whatsapp_notification(formatted_message)
                success = True
                logger.info("WhatsApp notification sent successfully")
            except Exception as e:
                logger.error(f"Failed to send WhatsApp notification: {str(e)}")
        
        return success

    def send_telegram_notification(self, message):
        """Send a notification via Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown'  # Enable Markdown formatting
        }
        response = requests.post(url, data=data)
        response.raise_for_status()

    def send_whatsapp_notification(self, message):
        """Send a notification via WhatsApp"""
        # Check if session is valid, if not, use visible browser
        use_headless = is_session_valid()
        
        # Use the phone number configured in settings
        return send_whatsapp_message(
            phone_number=self.whatsapp_phone,
            message=message,
            use_headless=use_headless  # Will use headless mode if session is valid, otherwise visible browser
        )