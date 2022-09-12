from BotImports import *

class BotSettings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setBotGame(self, ctx, *, game=None):
        await self.client.change_presence(activity=discord.Game(game))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setBotWatching(self, ctx, *, watching=None):
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=watching))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def externalModule(self, ctx, task=None, module=None):
        modules = await getExternalModules(self.client)
        if not task or not module and task!="names":
            await ctx.send("Please select a task: names, add, remove, load, unload, reload\nfollowed by name of a module")
            return
        print(task)
        if task=="names":
            await ctx.send(', '.join(i for i in modules))
            return

        if task=="add" or task=='remove':
            if task=='add':
                modules.append(module)
            elif task=="remove":
                modules.pop(module)
            await writeExternalModules(self.client, modules)
            return

        if task=='load':
            try:
                if module=='RaidCommands':
                    self.client.load_extension(module)
                else:
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
                if module=='RaidCommands':
                    self.client.unload_extension(module)
                else:
                    self.client.unload_extension('modules.'+module)
                print(f"{module} has been unloaded")
                await ctx.send(f"{module} has been unloaded")
            except Exception as error:
                print(f"Unable to unload {module}\nError: {error}")
                await ctx.send(f"Unable to unload {module}\nError: {error}")
        elif task == "reload":
            try:
                if module=='RaidCommands':
                    self.client.reload_extension(module)
                else:
                    self.client.reload_extension('modules.'+module)
                print(f"Reloaded {module}")
                await ctx.send(f"Reloaded {module}")
            except Exception as error:
                print(f"Unable to reload {module}\nError: {error}")
                await ctx.send(f"Unable to reload {module}\nError: {error}")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def ferro_say(self, ctx, channel:discord.TextChannel, *, msg:str):
        try:
            await channel.send(msg)
        except:
            await ctx.channel.send("Error sending the message. Could be permission issue...")


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def edit_message(self, ctx, msg_old:discord.Message, msg_new:discord.Message):
        await msg_old.edit(content=msg_new.content)

    
def setup(client):
    client.add_cog(BotSettings(client))