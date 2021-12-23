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
        if guildSettings["welcomeMessage"] == None:
            await ctx.send("Welcome message not yet set. Remember to set welcome message")
        

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWelcomeMessage(self, ctx, welcomeMessage:nextcord.Message=None):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        guildSettings["welcomeMessage"] = welcomeMessage.id if welcomeMessage else None
        guildSettings["welcomeMessageFromChannel"] = welcomeMessage.channel.id if welcomeMessage else None
        data[str(ctx.guild.id)] = guildSettings 
        writeJson(guildSettingsPath, data)
        await ctx.send(f"Welcome message set to: {welcomeMessage.jump_url if welcomeMessage else None}")
        

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendWelcomeMessage(self, ctx):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        welcomeMessageId = guildSettings["welcomeMessage"]
        if not welcomeMessageId:
            await ctx.send("No welcome message set")
            return
        welcomeMessageFromChannel = self.client.get_channel(guildSettings["welcomeMessageFromChannel"])
        welcomeMessage = await welcomeMessageFromChannel.fetch_message(welcomeMessageId)
        await ctx.send(welcomeMessage.content)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendWelcomeMessageOnMemberJoin(self, ctx, sendMessage:str="False"):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        if sendMessage.lower().capitalize=="False":
            guildSettings["sendWelcomeMessage"] = "False"
            await ctx.send("I will now send:")
        elif sendMessage.lower().capitalize=="True":
            guildSettings["sendWelcomeMessage"] = "True"
        data[str(ctx.guild.id)] = guildSettings
        writeJson(guildSettingsPath, data)
        


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWelcomeDmMessage(self, ctx, welcomeDmMessage:nextcord.Message=None):
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendWelcomeDmOnMemberJoin(self, ctx, sendMessage:bool=False):
        pass

def setup(client):
    client.add_cog(UserGuildJoin(client))