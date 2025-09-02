from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ping(self, ctx: commands.Context):
        ms = int(round(self.bot.latency * 1000))
        await ctx.reply(f"Command registered, latency: {ms} ms")

async def setup(bot):
    await bot.add_cog(Ping(bot))
