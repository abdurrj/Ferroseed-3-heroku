from nextcord import guild
from BotImports import *

class UserGuildJoin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWelcomeChannel(self, ctx, welcomeChannel:nextcord.TextChannel=None):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        guildSettings["welcomeChannel"] = str(welcomeChannel.id) if welcomeChannel else None
        data[str(ctx.guild.id)] = guildSettings
        writeJson(guildSettingsPath, data)
        await ctx.send(f"Welcome channel set to: `{welcomeChannel}`")
        if guildSettings["sendWelcomeMessage"] == "False":
            await ctx.send("Setting for sending welcome message is currently set to `false`. Remember to change it to `True` if you wish to send welcome message")
        

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWelcomeMessage(self, ctx, welcomeMessage:nextcord.Message=None):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        guildSettings["welcomeMessage"] = welcomeMessage
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendWelcomeMessageOnMemberJoin(self, ctx, sendMessage:bool=False):
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWelcomeDmMessage(self, ctx, welcomeDmMessage:nextcord.Message=None):
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendWelcomeDmOnMemberJoin(self, ctx, sendMessage:bool=False):
        pass

