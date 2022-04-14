from email.policy import default
import discord, json, random, pytz, asyncio, os, dotenv, ast, asyncpg, re, emoji, sys
import numpy as np
from discord.ext import commands, tasks
from discord.ext.commands import CommandOnCooldown, BadArgument
from discord import AllowedMentions
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Paths
ballListJson = 'data/ball_list.json'

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

standardPrefix = "fb!"

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

async def setPrefix(client, message, prefix):
    await client.db.execute('UPDATE ferroseed.guilds SET prefix=$1 WHERE guild_id=$2', prefix, message.guild.id)

async def getExternalModules(client):
    moduleResponse = await client.db.fetch('SELECT modules from ferroseed.external_modules WHERE bot_id = $1', 728539394386034749)
    return ast.literal_eval(moduleResponse[0].get("modules"))

async def writeExternalModules(client, data):
    await client.db.execute('UPDATE ferroseed.external_modules SET modules=$1 WHERE guild_id=$2',str(data), 728539394386034749)

def getJson(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        return data


def writeJson(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)