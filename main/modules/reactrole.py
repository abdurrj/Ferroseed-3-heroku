from BotImports import *

class reactrole(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener("on_raw_reaction_add")
    async def addRoleToUser(self, payload):
        guildId = payload.guild_id
        guild = self.client.get_guild(guildId)
        channel_id = ...
        reactionRoles = getJson(reactrolePath)


    def getGuildDictFromJson(reactionRoles):
        return 

def setup(client):
    client.add_cog(reactrole(client))