# Discord Bot for InStockTrades Damage Comics

![Version](https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000)\
<br>
This Bot will scrape InStockTrades for Comics under the Damage Category
then Notify User about new Comics Added to the Website.

## Tech Stack

![Python](https://img.shields.io/badge/-Python-000000?style=flat&logo=python)\
![MongoDB](https://img.shields.io/badge/-MongoDB-000000?style=flat&logo=mongodb)\
![Discord](https://img.shields.io/badge/-Discord-000000?style=flat&logo=discord)\
![Docker](https://img.shields.io/badge/-Docker-000000?style=flat&logo=docker)

## Requirements

Install Docker-Compose: [Docker]("https://docs.docker.com/compose/install/")\
Obtain a Discord Bot Token: [Discord]("https://discord.com/developers/applications/")\
Obtain the Channel ID you want the Bot to send the Alert to: [Where to find ID]("https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-")\
Allow all Privileged Gateway Intents in the Bot Settings: [Privileged Gateway Intents]("https://discordpy.readthedocs.io/en/latest/intents.html")\
Generate Invite Link for the Bot with the following Permissions (2733747731520): [Invite Link Generator]("https://discordapi.com/permissions.html")

## Installation

Clone the Repo

```shell
  $ git clone https://github.com/timo1227/Discord-ComicBook-Bot.git
```

Configure the docker-compose.yml file with your Discord Bot Token, Channel Id, and MongoDB Link

```
  environment:
```

## Run Locally

Start the Docker Container

```console
  docker-compose up -d
```

## Commands

```commands
  !start - Start the Bot
  !stop - Stop the Bot
```

<!-- Once in watchlist the Bot will check every  Minutes for new Comics and send a Message to the Channel you configured. -->

## Suggestions and Issues

### If you have any Suggestions or Issues please open an Issue on Github.
