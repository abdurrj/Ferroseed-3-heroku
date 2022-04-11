from BotImports import *

class UserGuildJoin(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def setWelcomeChannel(self, ctx, welcomeChannel:discord.TextChannel=None):
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
        

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def setWelcomeMessage(self, ctx, welcomeMessage:discord.Message=None):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        guildSettings["welcomeMessage"] = welcomeMessage.id if welcomeMessage else None
        guildSettings["welcomeMessageFromChannel"] = welcomeMessage.channel.id if welcomeMessage else None
        data[str(ctx.guild.id)] = guildSettings 
        writeJson(guildSettingsPath, data)
        await ctx.send(f"Welcome message set to: {welcomeMessage.jump_url if welcomeMessage else None}")
        

    @commands.command(hidden=True)
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


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def sendWelcomeMessageOnMemberJoin(self, ctx, sendMessage:str="False"):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        if sendMessage.lower().capitalize=="False":
            guildSettings["sendWelcomeMessage"] = "False"
            await ctx.send("I will not send a message announcing new members")
        elif sendMessage.lower().capitalize=="True":
            guildSettings["sendWelcomeMessage"] = "True"
            await ctx.send("I will now send a message announcing new members if you have set a channel and message")
        data[str(ctx.guild.id)] = guildSettings
        writeJson(guildSettingsPath, data)


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def setWelcomeDmMessage(self, ctx, welcomeDmMessage:discord.Message=None):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        guildSettings["welcomeDmMessage"] = welcomeDmMessage.id if welcomeDmMessage else None
        guildSettings["welcomeDmMessageFromChannel"] = welcomeDmMessage.channel.id if welcomeDmMessage else None
        data[str(ctx.guild.id)] = guildSettings 
        writeJson(guildSettingsPath, data)
        await ctx.send(f"Welcome message set to: {welcomeDmMessage.jump_url if welcomeDmMessage else None}")


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def sendWelcomeDmOnMemberJoin(self, ctx, sendMessage:str="False"):
        data = getJson(guildSettingsPath)
        guildSettings = data[str(ctx.guild.id)]
        if sendMessage.lower().capitalize=="False":
            guildSettings["sendWelcomeDm"] = "False"
            await ctx.send("I will not send a DM to new members")
        elif sendMessage.lower().capitalize=="True":
            guildSettings["sendWelcomeDm"] = "True"
            await ctx.send("I will now send a DM to new members if you have set a DM message.")
        data[str(ctx.guild.id)] = guildSettings
        writeJson(guildSettingsPath, data)


    ## Event listener

    @commands.Cog.listener("on_member_join")
    async def welcomeNewMemberEvent(self, member):
        pass

def setup(client):
    client.add_cog(UserGuildJoin(client))