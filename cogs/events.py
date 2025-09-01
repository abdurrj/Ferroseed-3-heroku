import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[bot] Logged in as {self.bot.user} (ID: {self.bot.user.id})")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        try:
            await thread.join()
            await thread.send("<a:ferropeek:755450581774106706>")
        except discord.Forbidden:
            print(f"[threads] Missing perms in thread {thread.id}")
        except Exception as e:
            print(f"[threads] Error for thread {thread.id}: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
