from BotImports import *


class moderation(commands.Cog): 
    def __init__(self, client):
        self.client = client
        self.guild = self.client.get_guild(12345)
        self.mutedRole = discord.utils.get(self.guild.roles, name="Muted")
        self.modLogsChannel = discord.utils.get(self.guild.channels, name="🔨┃mod-logs")

    @commands.command(name = 'purge', aliases=['clear', 'clean', 'p', 'c'])
    @commands.has_permissions(manage_messages = True)
    async def purge(self, ctx, amount=2):
        await ctx.channel.purge(limit=amount)
    
    @commands.command()
    @commands.has_permissions(manage_roles = True)
    async def smute (self, ctx, member: discord.Member, time, d, *, reason="None"):
        for channel in self.guild.channels:
            await channel.set_permissions(self.mutedRole, speak=False, send_messages=False, read_message_history=True, add_reactions=False, send_messages_in_threads=False, create_public_threads=False, create_private_threads=False)
        await member.add_roles(self.mutedRole)
        embed = await self.createMutedEmbed(d, member, reason, time)
        await self.modLogsChannel.send(embed=embed)
        await member.send(f"You have been muted for {reason} for {time}{d}")
        mute_duration = getMuteDuration(time, d)
        if mute_duration != 0:
            await asyncio.sleep(int(mute_duration))

        await member.remove_roles(self.mutedRole)
        embed = await self.createUnmuteEmbed(member)
        await self.modLogsChannel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unsmute (self, ctx, member: discord.Member):
        await member.remove_roles(self.mutedRole)
        embed = await self.createUnmuteEmbed(member)
        await self.modLogsChannel.send(embed=embed)
        await member.send(f"You have been unmuted from: {ctx.guild.name}")


    async def createMutedEmbed(self, d, member, reason, time):
        embed = discord.Embed(title="User Muted:", description=f"{member.mention} has been muted.", colour=discord.Colour.red(), timestamp=datetime.utcnow())
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.add_field(name="Mute Duration Remaining", value=f"{time}{d}", inline=False)
        return embed

    async def createUnmuteEmbed(self, member):
        return discord.Embed(title="User Unmuted:", description=f"Unmuted {member.mention}", colour=discord.Colour.green(), timestamp=datetime.utcnow())

async def setup(client):
    await client.add_cog(moderation(client))

def getMuteDuration(time, d):
    mute_duration = 0
    if d == "s":
        mute_duration = time
    if d == "m":
        mute_duration = time * 60
    if d == "h":
        mute_duration = time * 60 * 60
    if d == "d":
        mute_duration = time * 60 * 60 * 24
    return mute_duration