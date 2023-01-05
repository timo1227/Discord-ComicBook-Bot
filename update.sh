# !/bin/bash

# Update the system
sudo apt update && sudo apt upgrade -y
# Install the pip3
sudo apt install python3-pip -y
# Pip3 install the requirements
pip install discord
pip install requests
pip install bs4
pip install lxml
pip install python-dotenv

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