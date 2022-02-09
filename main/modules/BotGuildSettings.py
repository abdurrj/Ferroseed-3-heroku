from BotImports import *

class BotGuildSettings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener("on_guild_join")
    async def addGuildToJson(self, guild):
        data = getJson(guildSettingsPath)
        data[str(guild.id)] = {
            "prefix": standardPrefix,
            "welcomeChannel":None,
            "sendWelcomeMessage": "False",
            "welcomeMessage":None,
            "welcomeMessageFromChannel":None,
            "sendWelcomeDm": "False",
            "welcomeDmMessage":None,
            "welcomeDmFromChannel":None
        }

    @commands.Cog.listener("on_message")
    async def checkOrResetPrefix(self, message):
        if message.author == self.client.user:
            return
        
        # Ping bot for prefix
        if (self.client.user in message.mentions) and (len(message.content.split(" "))<2):
            if message.guild:
                await message.channel.send(f"My prefix is currently `{getPrefix(self.client, message)}`")

        # Type fb!reset to change prefix to "fb!" Can only be used by admins
        if message.content == "fb!reset" and message.author.guild_permissions.administrator == True:
            setPrefix(message)
            await message.channel.send(f"Prefix changed to fb!")

    @commands.command(hidden=True, aliases=["changeprefix", "changePrefix"])
    @commands.has_permissions(administrator=True)
    async def changeGuildPrefix(self, ctx, prefix):
        if (len(prefix.split(""))<5):
            setPrefix(ctx.message, prefix)
            await ctx.send(f"Prefix changed to `{prefix}`")
        else:
            await ctx.send("Prefix is too long. maximum 4 characters")

    @changeGuildPrefix.error
    async def changeGuildPrefixError(error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("I need to know what you want to change the prefix to.")
            
def setup(client):
    client.add_cog(BotGuildSettings(client))