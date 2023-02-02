FROM python:3.9
RUN pip install --upgrade pip
# Set working directory
WORKDIR /Discord-ComicBook-Bot
# Install dependencies
COPY . .
RUN pip install -r requirements.txt
CMD [ "python3" , "scrape_for_damages.py" ]