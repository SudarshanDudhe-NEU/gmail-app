import pywhatkit as kit
import datetime
import logging

def send_whatsapp_message(phone_number, message):
    """
    Send a WhatsApp message to the specified phone number.
    
    Args:
        phone_number (str): The recipient's phone number in the format "+1234567890".
        message (str): The message to send.
    """
    try:
        now = datetime.datetime.now()
        # Add 2 minutes to current time to allow WhatsApp Web to open
        wait_time = 2
        minutes = now.minute + wait_time
        hours = now.hour
        
        # Adjust hours if minutes exceed 59
        if minutes >= 60:
            hours = (hours + 1) % 24
            minutes = minutes % 60
            
        logging.info(f"Scheduling WhatsApp message to {phone_number} at {hours}:{minutes}")
        kit.sendwhatmsg(phone_number, message, hours, minutes)
        logging.info(f"WhatsApp message sent successfully to {phone_number}")
    except Exception as e:
        logging.error(f"Failed to send WhatsApp message: {e}")