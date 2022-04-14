from email.policy import default
import discord
import json, random, pytz, asyncio, os, dotenv, ast, asyncpg
from discord.ext import commands, tasks
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()



# Paths
guildSettingsPath = 'main/data/settings.json'
ballListJson = 'main/data/ball_list.json'
externalModulesPath = 'main/data/ext_modules.json'
userGreetingJson = 'main/data/user_greet.json'
# TOKEN = open('main/token.txt', 'r').readline()
TOKEN2 = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_HOST = os.getenv("DATABASE_HOST")

standardPrefix = "+-+"


## General methods
async def getPrefix(client, message):
    if not message.guild:
        return commands.when_mentioned_or(standardPrefix)(client, message)
    
    prefixResponse = await client.db.fetch('SELECT prefix from ferroseed.guilds WHERE guild_id = $1', message.guild.id)
    if len(prefixResponse) == 0:
        await client.db.execute('INSERT INTO ferroseed.guilds("guild_id", prefix) VALUES ($1, $2)', message.guild.id, standardPrefix)
        prefix = standardPrefix
    else:
        prefix = prefixResponse[0].get("prefix")

    return prefix

async def setPrefix(client, message, prefix=standardPrefix):
    await client.db.execute('UPDATE ferroseed.guilds SET prefix=$1 WHERE guild_id=$2', prefix, message.guild.id)

def getExternalModules():
    """Open json containing list of module names. Return list"""
    with open(externalModulesPath) as f:
        moduleList = json.load(f)
        return moduleList

def writeExternalModules(data):
    """Open json containing list of module names. Write data to json file"""
    with open(externalModulesPath) as f:
        json.dump(data, f)

def getJson(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        return data


def writeJson(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)