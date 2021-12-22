import nextcord
import json
from nextcord.ext import commands, tasks

# Paths
guildSettingsPath = 'main/data/settings.json'
externalModulesPath = 'main/data/ext_modules.json'
TOKEN = open('main/token.txt', 'r').readline()

standardPrefix = "fb!"


## General methods
def getPrefix(client, message):
    """Open json containing key (guild id) and value (guild specific settings).
    Read and return the prefix"""
    with open(guildSettingsPath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        guildSettings = data[str(message.guild.id)]
        return guildSettings["prefix"]

def setPrefix(message, prefix=standardPrefix):
    data = getJson(guildSettingsPath)
    guildSettings = data[str(message.guild.id)]
    guildSettings["prefix"] = prefix
    data[str(message.guild.id)] = guildSettings
    writeJson(guildSettingsPath, data)

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
        data = json.load(f)
        return data


def writeJson(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)