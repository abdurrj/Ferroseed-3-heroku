import nextcord
import json
from nextcord.ext import commands, tasks

# Paths
guildSettingsPath = 'main/data/settings.json'
externalModulesPath = 'main/data/ext_modules.json'
TOKEN = open('main/token.txt', 'r').readline()


## General methods
def getPrefix(client, message):
    """Open json containing key (guild id) and value (guild specific settings).
    Read and return the prefix"""
    with open(guildSettingsPath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        guildSettings = data[str(message.guild.id)]
        return guildSettings["prefix"]

def readExternalModules():
    """Open json containing list of module names. Return list"""
    with open(externalModulesPath) as f:
        moduleList = json.load(f)
        return moduleList

def writeExternalModules(data):
    """Open json containing list of module names. Write data to json file"""
    with open(externalModulesPath) as f:
        json.dump(data, f)

