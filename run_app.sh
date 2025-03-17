#!/bin/bash

# Add parent directory to Python path for imports
export PYTHONPATH=$(dirname $(realpath $0)):$PYTHONPATH

# Create required directories
mkdir -p logs data credentials

# Make sure log file exists and is writable
touch logs/gmail_monitor.log
chmod 666 logs/gmail_monitor.log

# Check if virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        # Try gmail-app-env instead
        if [ -d "gmail-app-env" ]; then
            source gmail-app-env/bin/activate
        else
            echo "Creating virtual environment..."
            python3 -m venv gmail-app-env
            source gmail-app-env/bin/activate
        fi
    fi
else
    echo "Virtual environment is already active: $VIRTUAL_ENV"
fi

# Install dependencies
pip install -r requirements.txt

# Check WhatsApp settings
if [ -f ".env" ] && grep -q "WHATSAPP_ENABLED=true" .env 2>/dev/null; then
    if [ ! -f "whatsapp_session_info.json" ]; then
        echo "WhatsApp is enabled but no session found."
        read -p "Initialize WhatsApp session now? (y/n): " initialize
        if [ "$initialize" = "y" ]; then
            python scripts/initialize_whatsapp.py
        fi
    else
        echo "WhatsApp session found."
    fi
else
    echo "WhatsApp not enabled or .env file not found."
fi

# Run the application
echo "Starting Gmail Monitor..."
python app.py