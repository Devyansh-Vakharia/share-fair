# ShareFair Bot

A Telegram bot for tracking and splitting expenses in group chats.

## Overview

ShareFair is a Telegram bot designed to help groups manage shared expenses. It reads the chat history to identify expenses, calculates totals, and creates fair settlement plans so everyone pays their share.

## Features

- **Expense Tracking**: Automatically extracts expense information from chat messages
- **Total Calculation**: Quickly get a summary of all expenses and the total amount
- **Fair Split**: Automatically calculates who owes whom to settle the expenses equally
- **Easy Interface**: Access functions through simple commands or interactive buttons

## Requirements

- Python 3.8+
- Telegram account with API access
- Google Gemini API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sharefair-bot.git
   cd sharefair-bot
   ```

2. Set up a Python virtual environment (using Poetry):
   ```
   poetry install
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   PHONE=your_phone_number
   BOT_API_TOKEN=your_bot_token
   GOOGLE_API_KEY=your_google_gemini_api_key
   ```

## Getting API Credentials

### Telegram API Credentials
1. Visit https://my.telegram.org/auth
2. Log in and go to "API development tools"
3. Create a new application
4. Note your API ID and API Hash
5. Create a bot with BotFather and get your BOT_API_TOKEN

### Google Gemini API Key
1. Go to https://ai.google.dev/gemini-api/docs/api-key
2. Create or select a project
3. Generate an API key

## Running the Bot

Use the provided shell script:
```
./cmd.sh start
```

Or run directly with Poetry:
```
poetry run python -m app.main
```

## Usage

1. Add the bot to your Telegram group
2. Mention expenses in the chat (e.g., "John paid $20 for pizza")
3. Use commands to manage expenses:

### Commands

- `/help` - Show the welcome message and available commands
- `/expense` - Show all expenses and the total amount
- `/split` - Calculate who owes whom to settle expenses equally

### Interactive Buttons

The bot also provides interactive buttons when sending the welcome message:
- **Expense** - Same as `/expense` command
- **Split** - Same as `/split` command

## How It Works

1. The bot reads all messages in the chat
2. It uses Google's Gemini AI to identify and extract expense information
3. For the `/expense` command, it lists all expenses and calculates the total
4. For the `/split` command, it creates a fair settlement plan to equalize payments

## Project Structure

- `app/main.py` - Main bot logic and event handlers
- `app/config.py` - Configuration loader
- `app/logger.py` - Logging setup
- `app/static_values.py` - Contains constants like welcome messages
- `.env` - Environment variables (not tracked in git)

## Limitations

- The bot needs to be added with appropriate permissions to read group messages
- A user account (via phone number) is required alongside the bot account to read message history
- Accuracy depends on how clearly expenses are mentioned in chat messages

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue in the repository.
