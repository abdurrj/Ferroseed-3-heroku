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
        modules = getExternalModules()
        if not task or not module:
            await ctx.send("Please select a task: names, add, remove, load, unload, reload\nfollowed by name of a module")
            return
        if task=="names":
            await ctx.send(', '.join(i for i in modules))
            return

        if task=="add" or task=='remove':
            if task=='add':
                modules.append(module)
            elif task=="remove":
                modules.pop(module)
            writeExternalModules(modules)
            return

        if task=='load':
            try:
                self.client.load_extension('modules.'+module)
                print(f"{module} has been loaded")
                await ctx.send(f"{module} has been loaded")
            except Exception as error:
                print(f"Unable to load {module}\nError: {error}")
                await ctx.send(f"Unable to load {module}\nError: {error}")
        elif task=='unload':
            if module=='BotSettings':
                await ctx.send(f"Cannot unload {module}. This module only supports \"reload\"")
                return
            try:
                self.client.unload_extension('modules.'+module)
                print(f"{module} has been unloaded")
                await ctx.send(f"{module} has been unloaded")
            except Exception as error:
                print(f"Unable to unload {module}\nError: {error}")
                await ctx.send(f"Unable to unload {module}\nError: {error}")
        elif task == "reload":
            try:
                self.client.reload_extension('modules.'+module)
                print(f"Reloaded {module}")
                await ctx.send(f"Reloaded {module}")
            except Exception as error:
                print(f"Unable to reload {module}\nError: {error}")
                await ctx.send(f"Unable to reload {module}\nError: {error}")

    
def setup(client):
    client.add_cog(BotSettings(client))