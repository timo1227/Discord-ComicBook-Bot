'''Get the Comics from the URL and insert current comic into the database'''
import time
import datetime
import discord
import typing
import asyncio
import functools
import aiohttp
import json
import sys
import motor.motor_asyncio
from os import environ
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()
# Connect to MONGODB
connection_url = environ["MONGO_URL"]
client = MongoClient(connection_url)
db = client.get_database('Comics')


# Discord Token from Dir 
TOKEN = environ["TOKEN"]
# Discord Channel ID
CHANNEL_ID = int(environ["CHANNEL_TEST"])
# Discord Client to send messages to the channel
client = discord.Client(intents=discord.Intents.all())
# Bool to check if the loop is running
loop_running = False

async def send_message(message):
    '''Send the message to the channel'''
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(message)

async def get_comics(url):
    '''Get the comics from the URL and insert current comic into the database'''
    total_damage = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            # get the data-max attribute from the input box with id="currentpage"
            pages = soup.find('input', {'id': 'currentpage'})
            pages = pages['data-max']
            print('Total pages:', pages)
            # Get comics from each page
            for page in range(1, int(pages) + 1):
                url = 'https://www.instocktrades.com/damages?pg='
                async with session.get(url + str(page)) as response:
                    html = await response.text()
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


async def loop_scrapping():
    '''Loop the scrapping function every 60 seconds'''
    while loop_running:
        try:
            await client.change_presence(activity=discord.Game(name='Scraping'))
            TOTAL = await get_comics('https://www.instocktrades.com/damages?pg=1')
            if loop_running:
                await client.change_presence(activity=discord.Game(name='Sleeping'))
            print('Updated at', datetime.datetime.now())
            print('Total Damage:', TOTAL)
            # Print the total number of comics in the database
            print('Total in database:', db.Damages.count_documents({}))
            # Sleep
            await asyncio.sleep(60)
            print("Slept for 60 seconds")
        except Exception as e:
            # If time out error sleep for 5 minutes
            if 'timed out' in str(e):
                # Send Message the will restart the loop in 5 minutes
                await send_message('Timed out, restarting in 5 minutes')
                await asyncio.sleep(300)
                # restart the loop
                await loop_scrapping()
            else:
                # Send the error to the channel
                await send_message(f'Error: {e}')
                # Kill the script
                loop_running = False
                # Set the status to waiting for !start
                await client.change_presence(activity=discord.Game(name='Waiting for !start'))
                return

# Command From Channel
@client.event
async def on_message(message):
    global loop_running
    # If the message is from the bot ignore it
    if message.author == client.user:
        return
    # If the message is not from the channel ignore it
    if message.channel.id != CHANNEL_ID:
        return
    # If the message is not !start ignore it
    if message.content == '!start' or message.content == '!Start':
        # Set global variable to true
        loop_running = True
        await loop_scrapping()
        return
    if message.content == '!stop' or message.content == '!Stop':
        # Break the while loop
        print('Stopping')
        loop_running = False
        await client.change_presence(activity=discord.Game(name='Waiting for !start'))
        return

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(CHANNEL_ID)
    # Set the status to waiting for !start  
    await client.change_presence(activity=discord.Game(name='Waiting for !start'))

    

# Run the bot
client.run(TOKEN)


# https://discord.com/api/oauth2/authorize?client_id=1059222457493487768&permissions=2733747731520&scope=bot