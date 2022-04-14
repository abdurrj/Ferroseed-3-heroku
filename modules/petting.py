from BotImports import *


pet_count_path = 'main/data/pet_count.json'
settings = 'main/data/settings.json'

async def readPetCountFromDb(client, guild_id):
    reactionRoleResponse = await client.db.fetch('SELECT ferro_pets from ferroseed.pet_count WHERE guild_id = $1', guild_id)
    if len(reactionRoleResponse) == 0:
        guild_dict = {"pet_stat":"random","chance":0.75,"Total pet":0,"Total hurt":0,"Members":{}}
        await writePetCountToDb(client, guild_id, guild_dict)
    else:
        guild_dict = ast.literal_eval(reactionRoleResponse[0].get("ferro_pets"))
        if type(guild_dict)=='tuple':
            guild_dict = guild_dict[0]

    return guild_dict

async def writePetCountToDb(client, guild_id, guild_dict):
    await client.db.execute('UPDATE ferroseed.pet_count SET ferro_pets=$1 WHERE guild_id=$2', str(guild_dict), guild_id)

class petting(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener("on_guild_join")
    async def guild_add(self, guild):
        guild_dict = {
            "pet_stat":"random",
            "chance":0.75,
            "Total pet":0,
            "Total hurt":0,
            "Members":{}
        }
        writePetCountToDb(self.client, guild.id, guild_dict)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def pet_random(self, ctx):
        embed = discord.Embed()
        embed.add_field(name="Would you like to always allow pets?", value="React with ✅ to always allow\nReact with ❌ to set to random")
        message = await ctx.send(embed=embed)
        emoji_list = ['✅','❌']
        guild_settings = await readPetCountFromDb(self.client, ctx.guild.id)
        for i in emoji_list:
            await message.add_reaction(i)

        def checker(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emoji_list

        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=15, check=checker)

                if str(reaction.emoji) == "✅":
                    guild_settings["pet_stat"] = "always"
                    await ctx.send("Pet settings changed to always allow pets")
                elif str(reaction.emoji) == "❌":
                    guild_settings["pet_stat"] = "random"
                    await ctx.send("Pet settings changed to randomize pets")

                await writePetCountToDb(self.client, ctx.guild.id, guild_settings)
                await message.delete()
                    
            except asyncio.TimeoutError:
                break

    @commands.command(description="You can try petting Ferroseed, though Iron Barbs might kick in and hurt you")
    async def pet(self, ctx):
        guild_dict = await readPetCountFromDb(self.client, ctx.guild.id)
        random = guild_dict["pet_stat"]
        Member_dict = guild_dict["Members"]
        if str(ctx.author.id) in Member_dict.keys():
            member = Member_dict[str(ctx.author.id)]
        else:
            Member_dict[str(ctx.author.id)] = {"pet":0, "hurt":0}
            member = Member_dict[str(ctx.author.id)]
        
        if random == "random":
            choices = ['pet', 'no pet']
            pet_chance = float(guild_dict["chance"])
            hurt_chance = float(1 - pet_chance)
            selection = np.random.choice(choices, 1, p=[pet_chance, hurt_chance])
        elif random == "always":
            selection = ['pet']

        if selection[0] == 'pet':
            total_pet = guild_dict["Total pet"]
            total_pet += 1
            guild_dict["Total pet"] = total_pet
            pet_count = member["pet"]
            pet_count += 1
            member["pet"] = pet_count
            embed = discord.Embed(
            colour = discord.Colour.green())
            embed.add_field(name='Ferroseed anticipated this', value=f"{ctx.author.mention} pet Ferroseed! <:ferroHappy:734285644817367050> \n"
                                                                        "\nYou have pet me **"+str(pet_count)+"x** times!")

        elif selection[0] == 'no pet':
            total_hurt = guild_dict["Total hurt"]
            total_hurt += 1
            guild_dict["Total hurt"] = total_hurt
            pet_hurt = member["hurt"]
            pet_hurt += 1
            member["hurt"] = pet_hurt
            embed = discord.Embed(
            colour = discord.Colour.red())
            embed.add_field(name='*Sorry!*', value=f"{ctx.author.mention} got hurt by Iron Barbs <:ferroSad:735707312420945940>\n"
                                                    "\nI've hurt you a total of **"+ str(pet_hurt) +"x** times.")

        Member_dict[str(ctx.author.id)] = member
        guild_dict["Members"] = Member_dict
        await writePetCountToDb(self.client, ctx.guild.id, guild_dict)
        await ctx.send(embed=embed)

    @pet.error
    async def pet_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            time = str(int(error.retry_after))
            await ctx.send(f"You can't pet me this often, you need to wait {time}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def pet_chance(self, ctx, value:float=0.75):
        """Change % chance of petting/getting hurt"""
        guild_dict = await readPetCountFromDb(self.client, ctx.guild.id)
        if value>=1 or value<0:
            await ctx.send("Enter a value between 0 and 1")
        else:
            guild_dict["chance"] = value
            await writePetCountToDb(self.client, ctx.guild.id, guild_dict)
            await ctx.send(f"Ferroseed has now **{value}%** chance of getting pet")


    @commands.command()
    async def pets_total(self, ctx):
        """Show server total pet and hurt count"""
        guild_dict = await readPetCountFromDb(self.client, ctx.guild.id)
        petcount = str(guild_dict["Total pet"])
        hurtcount = str(guild_dict["Total hurt"])
        embed = discord.Embed(colour=discord.Colour.green())
        embed.add_field(name=f"Hi {ctx.guild.name}", value="These are pet/hurt stats for this server!")
        embed.add_field(name="Total times pet on this server:", value=f"**{petcount}x** times", inline=False)
        embed.add_field(name="Total time I've hurt someone on this server", value=f"**{hurtcount}x** times", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def pets(self, ctx):
        """Show personal pet and hurt count"""
        guild_dict = await readPetCountFromDb(self.client, ctx.guild.id)
        Member_dict = guild_dict["Members"]
        if str(ctx.author.id) in Member_dict.keys():
            user_dict = Member_dict[str(ctx.author.id)]
            pet = str(user_dict["pet"])
            hurt = str(user_dict["hurt"])
            allowed_mentions = discord.AllowedMentions(users=False)
            await ctx.send(f"{ctx.author.mention}! you have pet me **{pet}x** times, and have been hurt **{hurt}x** times.", allowed_mentions=allowed_mentions)

    @commands.command()
    async def birbpet(self, ctx):
        """To pet the mint birb"""
        await ctx.send("<a:PetTheBirb:754269160598536214>")


def setup(client):
    client.add_cog(petting(client))  