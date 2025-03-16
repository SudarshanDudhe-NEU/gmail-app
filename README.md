# Gmail App

This project is a Gmail application that interacts with the Gmail API to perform various email-related tasks such as sending emails, searching messages, reading messages, and more.

## Project Structure

```
.
├── Dockerfile
├── Gmail
│   ├── cred2.json
│   ├── example.md
│   ├── gmail_actions.py
│   ├── gmail_auth.py
│   ├── gmail_utils.py
│   └── requirements.txt
├── README.md
├── auth
│   ├── __init__.py
│   ├── gmail_auth.py
├── check_old_emails.py
├── config
│   ├── __init__.py
│   └── settings.py
├── credentials.json
├── main.py
├── requirements.txt
├── run_app.sh
├── services
│   ├── __init__.py
│   ├── gmail_service.py
│   └── notification_service.py
├── src
│   ├── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   └── gmail_auth.py
│   ├── config
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── gmail_service.py
│   │   └── notification_service.py
│   └── utils
│       ├── __init__.py
│       └── email_parser.py
└── utils
    ├── __init__.py
    └── email_parser.py
```

## Dependencies

The project requires the following dependencies:

- `google-api-python-client>=2.100.0`
- `google-auth-httplib2>=0.1.0`
- `google-auth-oauthlib>=1.1.0`
- `python-dotenv>=1.0.0`
- `requests>=2.31.0`
- `pywhatkit>=5.4` (for WhatsApp notifications)
- `python-telegram-bot>=20.6` (for Telegram notifications)
- `transformers`
- `torch`

These dependencies are listed in the `requirements.txt` file.

## Running the Application

### Using Docker

1. **Build the Docker Image:**

   ```sh
   docker build -t gmail-app .
   ```

2. **Run the Docker Container:**

   ```sh
   docker run -d --name gmail-app --restart always gmail-app
   ```

   This will ensure that the container restarts automatically if it stops or if the system reboots.

### Using Docker Compose

1. **Create a `docker-compose.yml` file:**

   ```yaml
   version: "3"

   services:
     gmail-app:
       build: .
       restart: always
       volumes:
         - ./logs:/var/log/cron # Mount logs directory for persistence
   ```

2. **Start the Container with Docker Compose:**

   ```sh
   docker-compose up -d
   ```

### Running the Application Manually

1. **Install Dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

2. **Run the Application:**

   ```sh
   python main.py
   ```

## Authentication

The application uses OAuth 2.0 for authentication with the Gmail API. Ensure that you have the necessary credentials in the credentials.json file.

## Scripts

- run_app.sh: A script to run the application for 10 minutes and then kill it. This script is used by the cron job to run the application every hour.

## Cron Job

The Dockerfile sets up a cron job to run the run_app.sh script every hour. The cron job logs are stored in `/var/log/cron.log`.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
