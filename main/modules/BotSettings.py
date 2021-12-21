from os import write
from nextcord import activity
from BotImports import *

class BotSettings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setBotGame(self, ctx, *, game=None):
        await self.client.change_presence(activity=nextcord.Game(game))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setBotWatching(self, ctx, *, watching=None):
        await self.client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=watching))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def externalModule(self, ctx, task=None, module=None):
        modules = readExternalModules()
        if not task or not module:
            await ctx.send("Please select a task: names, add, remove, load, unload, reload\nfollowed by name of a module")
            return
        if task=="names":
            await ctx.send(', '.join(i for i in modules))
        elif task=="add":
            modules.append(module)
        elif task=="remove":
            modules.pop(module)

        writeExternalModules(modules)


    
def setup(client):
    client.add_cog(BotSettings(client))