#!/bin/bash

# Verify directory structure
mkdir -p logs data credentials

# Check if credentials exist
if [ ! -f "credentials/credentials.json" ]; then
  echo "WARNING: Gmail API credentials not found!"
  echo "You will need to set up credentials.json before authentication will work."
fi

# Check environment file
if [ ! -f ".env" ]; then
  echo "Creating .env file from example..."
  cp .env.example .env
  echo "Please edit .env with your settings before continuing."
fi

# Make scripts executable
chmod +x scripts/*.py
chmod +x run_app.sh
