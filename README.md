# Gmail Notification App

An application that monitors your Gmail inbox for important emails and sends notifications through Telegram or WhatsApp.

## Features

- Automatically detects important emails based on configurable criteria
- Sends notifications via Telegram (WhatsApp support planned)
- Customizable polling interval
- Secure authentication with Gmail API

## Setup Instructions

### Prerequisites

- Python 3.7+
- Google Cloud account with Gmail API enabled
- Telegram bot (for notifications)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your configuration (see `.env.example`)
4. Run the application:
   ```
   python main.py
   ```

### Configuration

Set the following environment variables in your `.env` file:

- `GMAIL_CREDENTIALS_FILE`: Path to your Gmail API credentials file
- `GMAIL_USER_EMAIL`: Your Gmail email address
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID
- `CHECK_INTERVAL_SECONDS`: Email checking interval in seconds

## License

[MIT](LICENSE)
