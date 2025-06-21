# Discord Bot

This project is a Discord bot that interacts with the Bungie API. It is designed to provide various functionalities related to Bungie games and services.

## Project Structure

```
discord-bot
├── src
│   ├── bot.py          # Main entry point for the Discord bot
│   └── utils
│       └── __init__.py # Utility functions and classes
├── .env                # Environment variables for sensitive information
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd discord-bot
   ```

2. **Create a `.env` file:**
   Populate the `.env` file with your Bungie API key, Discord bot token, and channel ID:
   ```
   BUNGIE_API_KEY=your_bungie_api_key
   BOT_TOKEN=your_bot_token
   CHANNEL_ID=your_channel_id
   ```

3. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the bot, execute the following command:
```
python src/bot.py
```

Make sure your bot is invited to your Discord server and has the necessary permissions to read and send messages.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the bot.