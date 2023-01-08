# Update the system
sudo apt update && sudo apt upgrade -y
# Install the pip3
sudo apt install python3-pip -y
# Pip3 install the requirements
pip install discord
pip install aiohttp
pip install cchardet
pip install aiodns
pip install aiohttp[speedups]
pip install bs4
pip install lxml
pip install python-dotenv