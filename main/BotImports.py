import nextcord
import json
from nextcord.ext import commands

guildSettingsPath = 'main/data/settings.json'
externalModulesPath = 'main/data/ext_modules.json'
TOKEN = open('main/token.txt', 'r').readline()



def getPrefix(client, message):
    with open(guildSettingsPath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        guildSettings = data[str(message.guild.id)]
        return guildSettings["prefix"]

def readExternalModules():
    with open(externalModulesPath) as f:
        moduleList = json.load(f)
        return moduleList

def writeExternalModules(data):
    with open(externalModulesPath) as f:
        json.dump(data, f)

