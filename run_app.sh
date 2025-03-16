#!/bin/bash

# Start the application in the background
python main.py &
APP_PID=$!

# Wait for 10 minutes
sleep 600

# Kill the application
kill $APP_PID