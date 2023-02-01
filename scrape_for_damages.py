"""Get the Comics from the URL and insert current comic into the database"""
import datetime
from os import environ
import asyncio
import aiohttp
import discord
import motor.motor_asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Connect to MONGODB
connection_url = environ["MONGO"]
client = motor.motor_asyncio.AsyncIOMotorClient(connection_url)
db = client.get_database("Comics")


# Discord Token from Dir
TOKEN = environ["TOKEN"]
# Discord Channel ID
CHANNEL_ID = int(environ["CHANNEL"])
# Discord Client to send messages to the channel
client = discord.Client(intents=discord.Intents.all())
# Bool to check if the loop is running
LOOP_RUNNING = False


async def send_message(message):
    """Send the message to the channel"""
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(message)


async def delete_old_documents():
    """Delete the documents older than 1 day"""
    # Scanning the database for old comics and removing the if older than 1 day
    async for document in db.Damages.find({}):
        # if the document is older than 1 day delete it
        if document["Last Updated"] < datetime.datetime.now() - datetime.timedelta(
            days=1
        ):
            db.Damages.delete_one({"Title": document["Title"]})


async def get_comics(url):
    """Get the comics from the URL and insert current comic into the database"""
    total_damage = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            # get the data-max attribute from the input box with id="currentpage"
            pages = soup.find("input", {"id": "currentpage"})
            pages = pages["data-max"]
            # Get comics from each page
            for page in range(1, int(pages) + 1):
                url = "https://www.instocktrades.com/damages?pg="
                async with session.get(url + str(page)) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    # Get all items
                    items = soup.find_all("div", {"class": "item"})
                    for item in items:
                        # Increment total damage
                        total_damage += 1
                        # Get Title Price and Discount
                        title = item.find("div", {"class": "title"}).text
                        # Price the first
                        price = item.find("div", {"class": "srp"}).text
                        discount = item.find("div", {"class": "discount"}).text
                        sale_price = item.find("div", {"class": "price"}).text
                        href = item.find("div", {"class": "title"}).find("a")["href"]
                        link = "https://www.instocktrades.com" + href
                        # Strip the price and discount
                        title = title.strip()
                        price = price.strip()
                        discount = discount.strip()
                        sale_price = sale_price.strip()
                        # If title contains 'Absolute' or 'Omnibus' enter into database else skip
                        if (
                            "Absolute" in title
                            or "Omnibus" in title
                            or title.find("omnibus") != -1
                            or title.find("absolute") != -1
                        ):
                            # Create Document
                            doc = {
                                "Title": title,
                                "Price": price,
                                "Discount": discount,
                                "Sale Price": sale_price,
                                "Link": link,
                                "Last Updated": datetime.datetime.now(),
                            }
                            # Check if the document already exists
                            if await db.Damages.count_documents({"Title": title}) == 0:
                                # Insert the document into the database
                                await db.Damages.insert_one(doc)
                                print("Inserted into database")
                                # Alert the user New Comic
                                message = f"**{title}**\nPrice: {price} Discount: {discount}\nSale Price: {sale_price}\nLink: {link}\n\n\n"
                                await send_message(message)
                            else:
                                # Update the document with the new data
                                await db.Damages.update_one(
                                    {"Title": title}, {"$set": doc}
                                )
    # When done return the total damage
    return total_damage


async def loop_scrapping():
    """Loop the scrapping function every 5 seconds"""
    global LOOP_RUNNING
    while LOOP_RUNNING:
        try:
            await client.change_presence(activity=discord.Game(name="Scraping"))
            total = await get_comics("https://www.instocktrades.com/damages?pg=1")
            if LOOP_RUNNING:
                await client.change_presence(activity=discord.Game(name="Sleeping"))
            print("Updated at", datetime.datetime.now())
            print("Total Damage:", total)
            # Print the total number of comics in the database
            print("Total in database:", await db.Damages.count_documents({}))
            # Delete old documents
            await delete_old_documents()
            # Sleep for 5 seconds
            await asyncio.sleep(5)
            print("Slept for 5 seconds")
        except Exception as error:
            # If time out error sleep for 5 minutes
            if "timed out" in str(error):
                # Send Message the will restart the loop in 2 minutes
                await send_message("Timed out, restarting in 2 minutes")
                await asyncio.sleep(120)
                # restart the loop
                await loop_scrapping()
            elif "Cannot write to closing transport" in str(error):
                # Send Message the will restart the loop in 2 minutes
                await send_message(
                    "Cannot write to closing transport, restarting in 2 minutes"
                )
                await asyncio.sleep(120)
                # restart the loop
                await loop_scrapping()
            else:
                # Send the error to the channel
                await send_message(f"Error: {error}")
                # Print the error
                print(error)
                # Kill the script
                LOOP_RUNNING = False
                # Set the status to waiting for !start
                await client.change_presence(
                    activity=discord.Game(name="Waiting for !start")
                )
                return


# Command From Channel
@client.event
async def on_message(message):
    """When a message is sent in the channel check if it is !start or !stop"""
    # If the message is from the bot ignore it
    if message.author == client.user:
        return
    # If the message is not from the channel ignore it
    if message.channel.id != CHANNEL_ID:
        return
    # If the message is not !start ignore it
    if message.content == "!start" or message.content == "!Start":
        # Set global variable to true
        global LOOP_RUNNING
        LOOP_RUNNING = True
        await loop_scrapping()
        return
    if message.content == "!stop" or message.content == "!Stop":
        # Break the while loop
        print("Stopping")
        LOOP_RUNNING = False
        await client.change_presence(activity=discord.Game(name="Waiting for !start"))
        return


@client.event
async def on_ready():
    """When the bot is ready print that we have logged in"""
    print(f"{client.user} has connected to Discord!")
    client.get_channel(CHANNEL_ID)
    # Set the status to waiting for !start
    await client.change_presence(activity=discord.Game(name="Waiting for !start"))


# Run the bot
client.run(TOKEN)


# https://discord.com/api/oauth2/authorize?client_id=1059222457493487768&permissions=2733747731520&scope=bot
