# Gmail Email Monitor

Monitor your Gmail inbox for important emails and receive notifications via Telegram and WhatsApp.

## Features

- **Automated Email Monitoring**: Continuously check for new emails or run one-time checks
- **Smart Filtering**: Identify important emails based on keywords and sender information
- **Multi-Channel Notifications**:
  - Telegram messages with formatted content
  - WhatsApp messages with both headless and visible browser modes
- **WhatsApp Integration**:
  - Headless operation (no browser window needed)
  - Session management with auto-reconnection
  - QR code scanning for initial setup
- **Robust Architecture**:
  - Modular Python codebase
  - Comprehensive logging
  - Persistent tracking of processed emails
- **Deployment Options**:
  - Run locally as a Python script
  - Deploy using Docker or Docker Compose
  - Schedule with cron

## Quick Start

### Prerequisites

- Python 3.7+
- A Gmail account
- A Telegram bot (optional for Telegram notifications)
- WhatsApp account (for WhatsApp notifications)

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/gmail-app.git
   cd gmail-app
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file based on .env.example:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Set up Gmail API credentials:

   - Visit the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable the Gmail API
   - Create OAuth credentials and download as credentials.json

5. Initialize WhatsApp (if using WhatsApp notifications):
   ```bash
   python scripts/initialize_whatsapp.py
   ```
   - Follow the prompts to scan the QR code with your phone

### Usage

**Start continuous monitoring:**

```bash
python app.py
```

**Run a one-time check for older emails:**

```bash
python check_old_emails.py
```

**Use the helper script for common operations:**

```bash
./run_app.sh
```

## Configuration

Edit your .env file to configure the application:

| Setting                  | Description                      | Example                |
| ------------------------ | -------------------------------- | ---------------------- |
| `GMAIL_USER_EMAIL`       | Your Gmail address               | example@gmail.com      |
| `TELEGRAM_BOT_TOKEN`     | Telegram bot token               | 1234567890:ABCDEF...   |
| `TELEGRAM_CHAT_ID`       | Telegram chat ID                 | 123456789              |
| `WHATSAPP_ENABLED`       | Enable WhatsApp notifications    | true                   |
| `WHATSAPP_PHONE`         | WhatsApp phone with country code | +1234567890            |
| `CHECK_INTERVAL_SECONDS` | Time between email checks        | 300                    |
| `MAX_RESULTS_PER_QUERY`  | Max emails to check per query    | 100                    |
| `IMPORTANCE_KEYWORDS`    | Keywords for important emails    | urgent,interview,job   |
| `LOG_LEVEL`              | Logging level                    | INFO                   |
| `LOG_FILE`               | Path to log file                 | logs/gmail_monitor.log |

## Docker Deployment

### Using Docker

```bash
# Build the image
docker build -t gmail-app .

# Run the container
docker run -d --name gmail-app \
  -v ./credentials:/app/credentials \
  -v ./logs:/app/logs \
  -v ./data:/app/data \
  --restart always \
  gmail-app
```

### Using Docker Compose

```bash
# Start with Docker Compose
docker-compose up -d
```

## Project Structure

```
gmail-app/
├── app.py                     # Main application entry point
├── check_old_emails.py        # One-time email checking script
├── auth/                      # Authentication modules
│   └── gmail_auth.py          # Gmail API authentication
├── config/                    # Configuration
│   └── settings.py            # Application settings
├── services/                  # Core services
│   ├── gmail_service.py       # Gmail API interactions
│   └── notification_service.py # Notification handling
├── utils/                     # Utility modules
│   ├── email_parser.py        # Email parsing utilities
│   └── whatsapp_notifications.py # WhatsApp messaging
├── scripts/                   # Utility scripts
│   ├── initialize_whatsapp.py # WhatsApp session setup
│   └── test_*.py              # Various test scripts
├── credentials/               # API credentials (gitignored)
├── data/                      # Persistent data
└── logs/                      # Log files
```

## Testing

The scripts directory contains several testing utilities:

```bash
# Test WhatsApp functionality
python scripts/test_whatsapp.py

# Test email checking
python scripts/test_email_checks.py

# Test notification delivery
python scripts/test_notifications.py
```

## WhatsApp Integration

This project includes robust WhatsApp messaging capabilities:

- **Session Management**: Auto-detect and refresh expired sessions
- **Headless Mode**: Send messages without visible browser window
- **Visible Mode**: Fallback to visible browser when needed for session refresh
- **Session Initialization**: Interactive script to set up WhatsApp Web session

To initialize or reinitialize a WhatsApp session:

```bash
python scripts/initialize_whatsapp.py
```

## Logging

Logs are stored in the logs directory and provide detailed information about:

- Email checking operations
- Important emails found
- Notification sending attempts
- Authentication status
- Errors and exceptions

## AI-Powered Email Classification

This application uses Llama 3.2, a powerful open-source language model, for intelligent email processing:

- **Smart Classification**: Automatically identifies important emails beyond simple keyword matching
- **Content Summarization**: Generates concise summaries for notifications
- **Context-Aware Analysis**: Understands email context for better importance scoring

### Setting Up Llama 3.2

1. Install Ollama (the Llama runtime):
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull the Llama 3.2 model:
   ```bash
   ollama pull llama3.2
   ```

3. Start the Ollama service:
   ```bash
   ollama serve
   ```

### Advanced Configuration Options

Add these to your `.env` file:

| Setting          | Description                              | Default |
|------------------|------------------------------------------|---------|
| `USE_LLAMA`      | Enable or disable Llama for classification | true    |
| `LLAMA_URL`      | URL for Ollama API                       | http://localhost:11434 |
| `SUMMARY_LENGTH` | Maximum length for email summaries       | 150     |

## Troubleshooting

### Fixing Authentication Issues

If you encounter OAuth errors like "invalid_grant" or "redirect_uri_mismatch":

1. Delete expired tokens:
   ```bash
   rm credentials/token*.json
   ```

2. Update Google Cloud Console settings:
   - Add both `http://localhost:8080` AND `http://localhost:8080/` (with trailing slash) as redirect URIs
   - Regenerate client secret if it was exposed

3. Run the application again to trigger the authentication flow

### Background Operation

Multiple options to keep the application running in the background:

#### Using nohup (simplest)
```bash
nohup run_app.sh > logs/output.log 2>&1 &
```

#### Using tmux (better for debugging)
```bash
# Install tmux
brew install tmux

# Start session
tmux new -s gmail-app
./run_app.sh
# Press Ctrl+B then D to detach

# Reattach later
tmux attach -t gmail-app
```

#### Using launchd (macOS system service)
Create a plist file at `~/Library/LaunchAgents/com.yourusername.gmail-app.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourusername.gmail-app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/your/run_app.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/your/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/your/logs/stderr.log</string>
</dict>
</plist>
```

Then load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.yourusername.gmail-app.plist
```

## Security Best Practices

1. **Protect your credentials**:
   - Add sensitive files to .gitignore:
     ```
     credentials/*.json
     whatsapp_session_info.json
     data/processed_emails.txt
     ```
   - Use environment variables instead of files when possible

2. **Regenerate compromised secrets**:
   - If you accidentally expose OAuth client secrets, regenerate them in Google Cloud Console
   - Store credentials outside the code repository

3. **Regular updates**:
   - Keep dependencies updated: `pip install --upgrade -r requirements.txt`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
