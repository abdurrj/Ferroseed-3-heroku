from BotImports import *

async def readAllBirthdaysFromDb(client):
    dob = await client.db.fetch('SELECT * from ferroseed.birthday')
    return dob

async def readUserBirthdayFromDb(client, user_id):
    dob = await client.db.fetch('SELECT date_of_birth from ferroseed.birthday where user_id = $1', user_id)
    return dob

async def writeUserBirthdayToDb(client, user_id, date_of_birth):
    print("trying to write")
    return await client.db.execute(
        'insert into ferroseed.birthday (user_id, date_of_birth) '+
        'values($1, $2) '+
        'ON CONFLICT (user_id) '+
        'DO UPDATE set date_of_birth = $2',
         user_id, date_of_birth
         )
    
def convertIsoDateStringToMonthAndDate(date_of_birth:str):
    return date.fromisoformat(date_of_birth).strftime('%B %d')

def checkdateInput(month:str, day:str):
    try:
        datestring = f"2000-{month}-{day}"
        dateobject = date.fromisoformat(datestring)
        return True
    except:
        print("error parsing date")
        return False


class Birthday(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["bdays"])
    async def getAllBdays(self, ctx):
        allowed_mentions = discord.AllowedMentions(users=False)
        result = await readAllBirthdaysFromDb(self.client)
        sorted_result = {user_id: date_of_birth for user_id, date_of_birth in sorted(result, key=lambda item: date.fromisoformat(item[1]))}
        message = ""
        for i in sorted_result:
            try:
                message = message + ctx.guild.get_member(i).mention + ": " + date.fromisoformat(sorted_result[i]).strftime('%B %d') + "\n"
            except:
                pass
        print(message)
        await ctx.send(message, allowed_mentions=allowed_mentions)

    @commands.command(aliases=["bday"])
    async def getBday(self, ctx, *user:discord.Member):
        if user:
            user = user[0].id
        else:
            user = ctx.message.author.id
        result = await readUserBirthdayFromDb(self.client, user)
        if len(result) == 1:
            dob = convertIsoDateStringToMonthAndDate(result[0]["date_of_birth"])
        else:
            dob = "can't find date of birth"
        await ctx.send(dob)
        

    @commands.command()
    async def setbday(self, ctx, month:str=None, day:str=None):
        failure_message = "Please provide date in mm-dd, like 01 31. Year won't be displayed and is not necessary."
        datestring = f"2000-{month}-{day}"
        if checkdateInput(month, day) == False:
            await ctx.send(failure_message)
            return
        result = await writeUserBirthdayToDb(self.client, ctx.message.author.id, datestring)
        if str(result) == "INSERT 0 1":
            dob = convertIsoDateStringToMonthAndDate(datestring)
            await ctx.send(f"Birthday set to {dob}")
        else:
            await ctx.send("Something went wrong, try again or check with my dad")


async def setup(client):
    await client.add_cog(Birthday(client))