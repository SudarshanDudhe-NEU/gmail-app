# Use the official Python image as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install build-essential and other necessary build tools
RUN apt-get update && \
    apt-get install -y build-essential gcc cron && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get remove -y build-essential gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY . .

# Make the run script executable
RUN chmod +x run_app.sh

# Set environment variables (if any)
ENV PYTHONUNBUFFERED=1

# Set up cron job to run the script every 3 hours
RUN echo "0 */3 * * * /app/run_app.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/app-cron && \
    chmod 0644 /etc/cron.d/app-cron && \
    crontab /etc/cron.d/app-cron

# Create log file
RUN touch /var/log/cron.log

# Start cron in foreground
CMD cron && tail -f /var/log/cron.log