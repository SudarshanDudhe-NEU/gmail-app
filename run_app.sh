#!/bin/bash
# filepath: /Users/sudarshan/Job and Prep/Projects/gmail-app/run_app.sh

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Initialize WhatsApp session if needed
if [ ! -f "whatsapp_session_info.json" ]; then
    echo "No WhatsApp session found. Initializing..."
    python scripts/initialize_whatsapp.py
fi

# Run the application
echo "Starting Gmail Monitor..."
python app.py