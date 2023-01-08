# !/bin/bash

# Check if the bot is running
if pgrep -x "python3" > /dev/null
then
    echo "Bot is running"
    echo "Killing bot"
    # Kill the bot
    pkill python3
fi

# Pull the latest version of the bot
git pull origin main --allow-unrelated-histories -f

# Check if .env exists in the directory
if [ -f .env ]; then
    echo "\n"
else
    bash requirements.sh
    echo ".env does not exist"
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
fi

echo "Update Complete"