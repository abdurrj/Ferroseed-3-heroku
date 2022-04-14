from discord.ext import commands
from random import randint, randrange
import json, discord


class Den(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    async def denlist(self, ctx):
        await ctx.send("<https://www.serebii.net/swordshield/maxraidbattledens.shtml>")


    @commands.command()
    async def newden(self, ctx, *args):
        if args:
            loc = args[0]
            if loc == "ioa":
                i = randint(94, 157)
            elif loc == "swsh":
                i = randint(1, 93)
            elif loc == "ct":
                i = randint(158, 197)
        else:
            i = randrange(197)
        await ctx.send("<https://www.serebii.net/swordshield/maxraidbattles/den"+str(i)+".shtml>")


    @commands.command()
    async def den(self, ctx, pkmn, *form_input):
        user = ctx.message.author.name
        with open(r"data/pokemon.json", "r") as read_file:
            data = json.load(read_file)
        pokemon = str((pkmn.lower()).title())
        wrong_den_message = "That's not a den, "+str(user)+"! <a:RBops2:718139698912034937>. Only from 1 to 197, or promo <a:RHype:708568633508364310>"
        if form_input:
            if (form_input[0].lower()).title() in ["Galarian", "Galar"]:
                pokemon = "Galarian " + pokemon
            else:
                pokemon = pokemon
        else:
            pokemon = pokemon

        possible_names = []
        for i in range(0, len(data)):
            pkmn_info = data[i]
            if pkmn_info['name'].startswith(pokemon):
                poke_name = pkmn_info['name']
                possible_names.append(poke_name)
        
        if len(possible_names) != 0:
            pokemon_lookup = possible_names[0]
        else:
            pokemon_lookup = "notarealpokemon"
        

        if pkmn.isnumeric():
            b = int(pkmn)
            if b >=1 and b <198:
                await ctx.send("<https://www.serebii.net/swordshield/maxraidbattles/den"+str(b)+".shtml>")
            else:
                await ctx.send(wrong_den_message)
        else:
            if pkmn.lower() == 'promo':
                await ctx.send("<https://www.serebii.net/swordshield/wildareaevents.shtml>")
            elif len(possible_names) != 0:
                for i in range(0, len(data)):
                    pkmn_info = data[i]
                    if pokemon_lookup in (pkmn_info.values()):
                        pokemon_name = pkmn_info["name"]
                        dens = pkmn_info["dens"]
                        sword_dens_list = dens["sword"]
                        shield_dens_list = dens["shield"]
                        if len(sword_dens_list) == 0:
                            sword_dens = "None"
                        else:
                            sword_dens = ', '.join("["+str(sword_dens_list[i])+"]" + "(https://www.serebii.net/swordshield/maxraidbattles/den"+str(sword_dens_list[i])+".shtml)" for i in range(0, len(sword_dens_list)) if len(sword_dens_list) is not None)
                        # sword_dens = ', '.join(sword_dens_list[i] for i in range(0, len(sword_dens_list)) if len(sword_dens_list) is not None)
                        
                        if len(shield_dens_list) == 0:
                            shield_dens = "None"
                        else:
                            shield_dens = ', '.join("["+str(shield_dens_list[i])+"]" + "(https://www.serebii.net/swordshield/maxraidbattles/den"+str(shield_dens_list[i])+".shtml)" for i in range(0, len(shield_dens_list)) if len(shield_dens_list) is not None)
                        # shield_dens = ', '.join(shield_dens_list[i] for i in range(0, len(shield_dens_list)) if len(shield_dens_list) is not None)
                        
                        dencheck = sword_dens + shield_dens
                        if dencheck == "":
                            print("No dens")
                            await ctx.send("Sorry, I can't find it in any den")
                        else:
                            dens = pokemon_name.title() + " is in these dens:\nSword: " + sword_dens + "\nShield: " + shield_dens
                            embed = discord.Embed(title=pokemon_name.title())
                            embed.add_field(name="Sword dens:", value=sword_dens, inline=False)
                            embed.add_field(name="Shield dens:", value=shield_dens, inline=False)
                            await ctx.send(embed=embed)
            else:
                await ctx.send(wrong_den_message + " " + 'Or if you ment a galarian form, please write "pokemon_name galarian"')


def setup(client):
    client.add_cog(Den(client))
