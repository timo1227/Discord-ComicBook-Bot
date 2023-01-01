'''Get the Comics from the URL and insert current comic into the database'''
import time
import datetime
import discord
import typing
import asyncio
import functools
import requests
from bs4 import BeautifulSoup

# Connect to MONGODB
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.Comics
# Get HTML
URL = 'https://www.instocktrades.com/damages?pg=1'

# Discord Token from Dir 
TOKEN = open('PATH_TO_TOKEN', 'r').read()
# Discord Channel ID
CHANNEL_ID = int(open('PATH_TO_CHANNEL_ID', 'r').read())
# Discord Client to send messages to the channel
client = discord.Client(intents=discord.Intents.default())

async def send_message(message):
    '''Send the message to the channel'''
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(message)

async def get_comics(url):
    '''Get the comics from the URL and insert current comic into the database'''
    total_damage = 0
    # Get total number of pages
    response = requests.get(url, timeout=5)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    # get the data-max attribute from the input box with id="currentpage"
    pages = soup.find('input', {'id': 'currentpage'})
    pages = pages['data-max']
    print('Total pages:', pages)
    # Get comics from each page
    for page in range(1, int(pages) + 1):
        url = 'https://www.instocktrades.com/damages?pg='
        # print('New URL:', url + str(page))
        response = requests.get(url + str(page), timeout=5)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # Get all items
        items = soup.find_all('div', {'class': 'item'})
        for item in items:
            # Increment total damage
            total_damage += 1
            # Get Title Price and Discount
            title = item.find('div', {'class': 'title'}).text
            # Price the first
            price = item.find('div', {'class': 'srp'}).text
            discount = item.find('div', {'class': 'discount'}).text
            sale_price = item.find('div', {'class': 'price'}).text
            href = item.find('div', {'class': 'title'}).find('a')['href']
            link = 'https://www.instocktrades.com' + href
            # Strip the price and discount
            title = title.strip()
            price = price.strip()
            discount = discount.strip()
            sale_price = sale_price.strip()
            # Print the data for TESTING
            # print('Title:', title)
            # print('Price:', price)
            # print('Discount:', discount)
            # print('Sale Price:', sale_price)
            # print('Link:', 'https://www.instocktrades.com' + href)

            # If title contains 'Absolute' or 'Omnibus' enter into database else skip
            if 'Absolute' in title or 'Omnibus' in title:
                # Create Document
                doc = {
                    'Title': title,
                    'Price': price,
                    'Discount': discount,
                    'Sale Price': sale_price,
                    'Link': link,
                    'Last Updated': datetime.datetime.now()
                }
                # Check if the document already exists
                if db.Damages.find_one({'Title': title}) is None:
                    # Insert the document
                    db.Damages.insert_one(doc)
                    print('Inserted into database')
                    # Alert the user New Comic
                    message = f"**{title}**\nPrice: {price} Discount: {discount}\nSale Price: {sale_price}\nLink: {link}\n\n\n"
                    await send_message(message)
                else:
                    # Update the document with the new data
                    db.Damages.update_one({'Title': title}, {'$set': doc})

            # Scanning the database for old comics and removing the if older than 5 day
            for document in db.Damages.find():
                if document['Last Updated'] < datetime.datetime.now() - datetime.timedelta(days=5):
                    print('Removing:', document['Title'])
                    db.Damages.delete_one({'Title': document['Title']})

    return total_damage

def to_thread(func: typing.Callable) -> typing.Coroutine:
    '''Run a blocking function in a thread'''
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
    return wrapper

@to_thread
def BlockingSleep():
    '''Sleep for 60 seconds'''
    time.sleep(60)

async def run_blocking():
    '''Run the blocking function'''
    while True:
        TOTAL = await get_comics(URL)
        print('Updated at', datetime.datetime.now())
        print('Total Damage:', TOTAL)
        # Print the total number of comics in the database
        print('Total in database:', db.Damages.count_documents({}))
        # Sleep for 60 seconds
        await BlockingSleep()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('Online and Starting Up...')
    time.sleep(5)
    # Delete the last message
    async for message in channel.history(limit=1):
        await message.delete()
    # Run the blocking function
    await run_blocking()
    

# Run the bot
client.run(TOKEN)



# https://discord.com/api/oauth2/authorize?client_id=1059222457493487768&permissions=274877908992&scope=bot