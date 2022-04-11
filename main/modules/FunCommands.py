from ast import alias
from BotImports import *

class FunCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ferroHappyEmoji = "<:ferroHappy:734285644817367050>"
        self.rPartyEmoji = "<:RParty:706007725070483507>"
        self.rBopsLeftEmoji = "<a:RBops:718139734693773330>"
        self.noMentionsAllowed = discord.AllowedMentions(user=False, roles=False,everyone=False)

    @commands.command(
        name='caught',
        aliases=['c', 'catch', 'CATCH', 'CATCH!', 'catch!', 'CAUGHT', 'CAUGHT!', 'caught!']
        )
    async def pokemonCaught(self, ctx, *ball):
        ballList = getJson(ballListJson)
        pokeballEmoji = '<:xPoke:764576089275891772>'
        colour = self.getRandomEmbedColourFromSelection()
        ballEmoji = pokeballEmoji
        if ball:
            ball = str(ball[0])
            if ball in ballList.values():
                ballEmoji = ball
            elif ball.lower in ballList.keys():
                ballEmoji = ballList[ball.lower]

        embed = discord.Embed(
            colour = colour)
        embed.add_field(
            name=ballEmoji + " Caught!",
            value= self.rPartyEmoji + " <@"+str(ctx.author.id)+"> has caught the pokemon! " + self.rPartyEmoji, 
            inline=True)

        sentEmbedMessage = await ctx.send(embed=embed)

        await sentEmbedMessage.add_reaction(self.ferroHappyEmoji)
        await sentEmbedMessage.add_reaction("<:sayHeart:741079360462651474>")
        if ballEmoji!=pokeballEmoji:
            await sentEmbedMessage.add_reaction(ballEmoji)

    def getRandomEmbedColourFromSelection(self):
        colour = random.choice([
                0x96e6ff, # Light blue
                0x62eb96, # Light green
                0x9662eb, # Purple
                0xffe36f, # Yellow 
                0xe5e5e5, # White
                0xf7b897, # Peach
                0xffb3ba, # Pink
                0x21b1ff, # Blue
                0xffd732  # Honey yellow
            ])
        return colour
        
    @commands.command(pass_context=True, name = 'naught', aliases=['not'])
    async def pokemonNotCaught(self, ctx):
        embed = discord.Embed(
            colour = discord.Color.red())
        embed.add_field(name='<:sherbSad:732994987683217518> escaped', value="<@"+str(ctx.author.id)+"> did not catch the pokemon.", inline=True)
        sentEmbedMessage = await ctx.send(embed=embed)
        await sentEmbedMessage.add_reaction("<:ferroSad:735707312420945940>")

    @commands.command(name='hi', aliases=['hello'])
    async def ferroSayHi(self, ctx):
        data = getJson(userGreetingJson)
        response=self.ferroHappyEmoji
        if str(ctx.author.id) in data.keys() and data[str(ctx.auhtor.id)]:
            response = data[str(ctx.author.id)]
        await ctx.send(response, allowed_mentions = self.noMentionsAllowed)

    @commands.command(name = 'hi_response', aliases = ['set_hi', 'set_hi_response', 'hi_set'])
    async def setUserPreferredHiResponse(self, ctx, *, hiResponse:str=None):
        data = getJson(userGreetingJson)
        data[str(ctx.author.id)] = hiResponse
        if not hiResponse:
            hiResponse = self.ferroHappyEmoji
        await ctx.send(f"{ctx.author.mention}, I will now respond to `{getPrefix}hi` with {hiResponse}", allowed_mentions = self.noMentionsAllowed)

    @commands.command(name = 'sleep', aliases=['powernap', 'nap'])
    async def sendGoToSleepMessage(self, ctx, string):
        await ctx.send(f"Go to sleep, {string if string else ctx.author.mention} {self.rBopsLeftEmoji}", allowed_mentions = self.noMentionsAllowed)
    
    @commands.command(name = 'work', aliases=['homework'])
    async def sendWorkMessage(self, ctx, string:str=None):
        isProductiveMessage = random.choice(True,False)
        string = string if string else ctx.author.mention
        if isProductiveMessage:
            outgoingMessage = f"<a:RBops:718139734693773330> {string}! Go be productive."
        else:
            outgoingMessage = f"{string}! Go do the things. <:RStudy:762627515747008512>"
        await ctx.send(outgoingMessage, allowed_mentions=self.noMentionsAllowed)

    @commands.command()
    async def absleep(self, ctx):
        embed = discord.Embed(colour=discord.Colour.green())
        if ctx.author.id in [138411165075243008]:
            embed.add_field(name="*Abdur is going to sleep*", value=":zzz: :zzz: :zzz:")
        else:
            embed.add_field(name = "ABDUR!!", value=f"Go to sleep! {self.rBopsLeftEmoji}")
        await ctx.send(embed=embed)

    @commands.command()
    async def time(self, ctx):
        timezoneList = ['Singapore', 'Europe/Oslo', 'Europe/Lisbon','Canada/Newfoundland', 'US/Eastern', 'US/Central','US/Pacific']
        timezoneNames = ['Malaysia', 'Central Europe', 'West Europe', 'Newfoundland', 'US Eastern', 'US Central', 'US Pacific']
        timezoneNameAndTime = []

        for i in range(0, len(timezoneList)):
            timezone = pytz.timezone(timezoneList[i])
            timezoneName = timezoneNames[i]
            timezoneHour = datetime.now(timezone).strftime("%H")
            

    def addEmojiToTimeIfTimeIsBetweenTenPmAndFiveAm(hour:int, timezone):
        rowletSleepEmoji = ". <a:RSleep:718830355381223444>"
        time = datetime.now(timezone).strftime("")


def setup(client):
    client.add_cog(FunCommands(client))