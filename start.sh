# !/bin/bash

# Check if the bot is running
if pgrep -x "python3" > /dev/null
then
    echo "Bot is running"
    echo "Killing bot"
    # Kill the bot
    pkill python3
fi

# Check if .env exists in the directory
if [ -f .env ]; then
    echo ""
else
    echo "Creating .env"
    # create the .env file
    touch .env
    # Ask user for the token
    echo "Enter token:"
    read token
    # Write the token to the .env file
    echo "TOKEN=$token" >> .env
    # Ask user for channel id
    echo "Enter channel id:"
    read channel
    # Write the channel id to the .env file
    echo "CHANNEL=$channel" >> .env
    # Ask user for MongoDB connection string
    echo "Enter MongoDB connection string:"
    read mongo
    # Write the MongoDB connection string to the .env file
    echo "MONGO=$mongo" >> .env
fi

# Start the bot
python3 scrape_for_damages.py