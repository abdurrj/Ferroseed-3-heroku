from BotImports import *
from modules.HostedRaid import HostedRaid


raidStartChannelName = "start-raid"
raidJoinChannelName = "join-raid"
raidStartReactions = ['<:xPoke:764576089275891772>', '🔒', '❌']
raidStartReactionNames = ['xPoke', '🔒', '❌']
pokeballReaction = '<:xPoke:764576089275891772>'

class RaidFunctions(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ongoingRaids = []

    @commands.command(aliases=['startraid'])
    async def createRaidStartMessage(self, ctx, *, text:str):
        guild = ctx.guild
        requestChannel = ctx.channel
        raidStartChannel = discord.utils.get(guild.channels, name=raidStartChannelName)
        host = ctx.author

        if requestChannel != raidStartChannel:
            return

        if self.userAlreadyHostingRaid(ctx):
            await ctx.send("You can only host one raid at the time")
            return

        raidStartMessage = await raidStartChannel.send("This is a test message")
        for i in raidStartReactions:
            await raidStartMessage.add_reaction(i)

        maxNumberOfPlayers = getMaxNumberOfPlayers(text)
        text = text.replace(f"max {maxNumberOfPlayers}", "")
        channelDescription = getChannelDescription(text)
        text = text.replace(f'"{channelDescription}"', "")
        text = text.strip()
        channelName = text.replace(" ", "-")

        raid = HostedRaid(raidStartMessage, host, maxNumberOfPlayers, False, channelName, channelDescription)
        self.ongoingRaids.append(raid)


    @commands.Cog.listener("on_raw_reaction_add")
    async def createRaidChannel(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        reactor = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)

        if reactor == self.client.user:
            return

        raidStartChannel = discord.utils.get(guild.channels, name=raidStartChannelName)
        message = await raidStartChannel.fetch_message(payload.message_id)

        if payload.emoji.name not in raidStartReactionNames:
            await message.remove_reaction(payload.emoji, reactor)

        if payload.channel_id != raidStartChannel.id:
            return

        raidCategory = raidStartChannel.category

        message = await raidStartChannel.fetch_message(payload.message_id)
        raid = None
        for i in self.ongoingRaids:
            if message == i.raidStartMessage and i.raidHost == reactor:
                raid = i
                break

        if raid == None:
            await message.remove_reaction(payload.emoji, reactor)
            return

        if raid.raidChannel:
            return

        if payload.emoji.name == '❌':
            await message.delete()
            indexOfRaid = self.ongoingRaids.index(raid)
            self.ongoingRaids.remove(indexOfRaid)
            return

        if payload.emoji.name != 'xPoke':
            return

        for i in message.reactions:
            if i.emoji == '🔒' and i.count > 1:
                raid.isLocked = True
                break

        raidJoinChannel = discord.utils.get(guild.channels, name="join-raid")
        raidJoinMessage = await raidJoinChannel.send("React here to join raid")
        await raidJoinMessage.add_reaction(pokeballReaction)
        hostedRaidChannel = await guild.create_text_channel(raid.channelName, category=raidCategory, topic=raid.channelDescription)
        await self.setRaidChannelPermissions(guild, hostedRaidChannel, raid)

        raid.raidChannel = hostedRaidChannel
        raid.raidJoinMessage = raidJoinMessage


    async def setRaidChannelPermissions(self, guild, hostedRaidChannel, raid):
        await hostedRaidChannel.set_permissions(guild.default_role, send_messages=False)
        await hostedRaidChannel.set_permissions(self.client.user, send_messages=True) # Not necessary if bot is admin, ferro isn't
        await hostedRaidChannel.set_permissions(raid.raidHost, send_messages=True)

    @commands.Cog.listener("on_raw_reaction_add")
    async def joinRaid(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        raidJoinChannel = discord.utils.get(guild.channels, name=raidJoinChannelName)

        if payload.channel_id != raidJoinChannel.id:
            return

        reactor = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
        if reactor == self.client.user:
            return

        if payload.emoji.name != 'xPoke':
            return

        message = await raidJoinChannel.fetch_message(payload.message_id)

        raid = self.getRaidForJoinMessage(message)
        if not raid or reactor == raid.raidHost:
            return

        if raid.isLocked or raid.isFull():
            await message.remove_reaction(pokeballReaction, reactor)
            return

        raid.participants.append(reactor)

        await raid.raidChannel.set_permissions(reactor, send_messages=True)
        await raid.raidChannel.send(f"{reactor.mention} just joined!")
        raid.currentUsers +=1

    @commands.Cog.listener("on_raw_reaction_remove")
    async def leaveRaidByReaction(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        raidJoinChannel = discord.utils.get(guild.channels, name=raidJoinChannelName)

        if payload.channel_id != raidJoinChannel.id:
            return

        if payload.emoji.name != 'xPoke':
            return

        message = await raidJoinChannel.fetch_message(payload.message_id)
        reactor = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
        raid = self.getRaidForJoinMessage(message)
        if raid and not reactor == raid.raidHost:
            currentRaiders = raid.currentUsers
            await self.leaveRaid(reactor, raid)
            if currentRaiders > raid.currentUsers: # To avoid getting notification when bot removes reaction when raid is full / locked
                await raid.raidChannel.send(f"{reactor.name} has left the raid")


    @commands.command(aliases=["leave"])
    async def leaveRaidByCommand(self, ctx):
        for i in self.ongoingRaids:
            if i.raidChannel == ctx.channel:
                await self.leaveRaid(ctx.author, i)
                await ctx.send(f"{ctx.author.name} has left")

    @commands.command(aliases=["end"])
    async def endRaid(self, ctx):
        raid = self.getRaidFromContext(ctx)

        if not raid or raid.raidHost != ctx.author:
            return
        for i in raid.participants:
            await i.raidChannel.set_permissions(i, send_messages=False)
        await raid.raidChannel.send("This raid has now ended. Thank you for hosting!")
        await raid.raidChannel.set_permissions(ctx.author, send_messages=False)
        await asyncio.sleep(240) # three min before channel remove?
        await raid.raidJoinMessage.delete()

    @commands.command(aliases=["lock"])
    async def switchRaidLockStatus(self, ctx):
        raid = self.getRaidFromContext(ctx)
        if not raid or raid.raidHost != ctx.author:
            return
        isLocked = raid.switchRaidLockStatus()
        if isLocked:
            await ctx.send("Raid is now locked")
        else:
            await ctx.send("Raid is now unlocked")

    @commands.command(aliases=["deleteAllRaids"])
    @commands.has_permissions(administrator=True)
    async def deleteAllOngoingRaids(self, ctx):
        for raid in self.ongoingRaids:
            try:
                await raid.raidChannel.delete()
            except:
                print("couldn't delete raid channel")
            try:
                await raid.raidJoinMessage.delete()
            except:
                print("couldn't delete raid message")
        self.ongoingRaids.clear()


    @commands.command(aliases=["max"])
    async def changeMaximumRaiders(self, ctx, newMax:int):
        raid = self.getRaidFromContext(ctx)
        if not raid or raid.raidHost != ctx.author and raid.raidChannel == ctx.channel:
            return
        raid.maxUsers = newMax
        await ctx.send(f"New maximum has been set to **{newMax}**")

    @commands.command(aliases=["number"])
    async def checkCurrentRaiders(self, ctx):
        raid = self.getRaidFromContext(ctx)
        if not raid or raid.raidChannel != ctx.channel:
            return
        await ctx.send(f"There are currently {raid.currentUsers} raiders here.")

    @commands.command(aliases=["pin"])
    async def pinPreviousHostMessageToRaid(self, ctx):
        raid = self.getRaidFromContext(ctx)
        if not raid or raid.raidHost != ctx.author and raid.raidChannel == ctx.channel:
            return
        messages = [message async for message in ctx.channel.history(limit=123)]
        authorMessages = list(filter(lambda m: m.author.id == ctx.author.id and m != ctx.message, messages))
        messageToPin = authorMessages[0]
        raid.pinnedMessages.append(messageToPin)
        await messageToPin.pin()
        await ctx.send(f"Message pinned. use command unpin {len(raid.pinnedMessages)} to remove it")


    @commands.command(aliases=["unpin"])
    async def unPinMessageFromIndex(self, ctx, number:int):
        number -= 1
        raid = self.getRaidFromContext(ctx)
        if not raid or raid.raidHost != ctx.author and raid.raidChannel == ctx.channel:
            return
        await raid.pinnedMessages[number].unpin()
        await ctx.send("Message has been unpinned")

    def getRaidFromContext(self, ctx):
        for i in self.ongoingRaids:
            if i.raidChannel == ctx.channel:
                return i
        return None

    def getRaidForJoinMessage(self, message):
        raid = None
        for i in self.ongoingRaids:
            if i.raidJoinMessage == message:
                raid = i
                break
        return raid

    async def leaveRaid(self, reactor:discord.Member, raid:HostedRaid):
        raid.currentUsers -= 1
        await raid.raidChannel.set_permissions(reactor, send_messages=False)
        await raid.raidJoinMessage.remove_reaction(pokeballReaction, reactor)
        index = raid.participants.index(reactor)
        del raid.participants[index]

    def userAlreadyHostingRaid(self, ctx):
        userHasRaid = False
        for raid in self.ongoingRaids:
            if ctx.author == raid.raidHost:
                userHasRaid = True
        return userHasRaid

async def setup(client):
    await client.add_cog(RaidFunctions(client))

def getMaxNumberOfPlayers(text:str):
    maxNumberOfPlayers = 20
    maxPlayerMatch = re.search("max (\d+)", text)
    if maxPlayerMatch:
        maxNumberOfPlayers = maxPlayerMatch.group(1)
    return maxNumberOfPlayers

def getChannelDescription(text:str):
    description = None
    if text.count('"') == 2:
        contentList = text.split('"', 2)
        description = contentList[1]
    return description