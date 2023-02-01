FROM python:3.9
RUN pip install --upgrade pip
# Set working directory
WORKDIR /Discord-ComicBook-Bot
# Install dependencies
COPY . .
RUN pip install -r requirements.txt
# Pull the latest from git
# Run the Entry Point
ENTRYPOINT ["bash", "start.sh"]