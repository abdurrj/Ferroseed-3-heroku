from cogs.PokeApiConsumer import *


regionForms = ["alolan", "galarian", "hisuian", "paldean", "paldean-fire", "paldean-water"]
rotomForms = ["fan", "frost", "heat", "mow", "wash"]
calyrexForms = ["ice-rider", "shadow-rider"]
darmanithanForms = ["standard", "zen"]
genderForms = ["male", "female", "f", "m"]
temporaryForms = ["mega", "mega-x", "mega-y", "gigantamax"]

class Dexter(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["sprites", "newsprite"])
    async def spriteNew(self, ctx, *, pkmn:str):
        pkmn = pkmn.lower()
        isShiny = checkIfShinySpriteRequest(pkmn)
        formFound, formRequested = checkIfFormRequested(pkmn)
        if formFound:
            pkmn = pkmn.replace(formRequested, "").strip()
        if isShiny:
            pkmn = pkmn.replace("shiny", "").replace("*", "").strip()

        pokemonData = pokemonLookUp(pkmn, formFound)
        if formFound and formFound.lower() not in pokemonData['name'].lower():
            return
        genderDifference = False
        if not pokemonData['name'].lower().startswith("basculegion"):
            genderDifference = await hasGenderDifference(pokemonData["dexId"])
        url, urlBack, urlFemale, urlFemaleBack = generatePictureUrl(pokemonData["name"], isShiny, genderDifference, pokemonData["generation"])
        hasBackSprites = requests.head(urlBack).status_code == 200
        await sendSprites(ctx, genderDifference, hasBackSprites, url, urlBack, urlFemale, urlFemaleBack)


    @commands.command()
    async def sprite(self, ctx, pkmn, *shiny):
        with open(r"data/pokemon.json", "r") as read_file:
            data = json.load(read_file)
        pokemon = str((pkmn.lower()).title())
        possible_names = []
        for i in range(0, len(data)):
            pkmn_info = data[i]
            if pkmn_info['name'].startswith(pokemon):
                poke_name = pkmn_info['name']
                possible_names.append(poke_name)
        if len(possible_names) == 0:
            print("No match")
        else:
            pokemon = possible_names[0]
            
        for i in range(0, len(data)):
            pokemon_dict = data[i]
            if pokemon in (pokemon_dict.values()):
                if shiny:
                    if shiny[0] == "*" or shiny[0].lower() == "shiny":
                        folder = "shiny"
                    else:
                        folder = "normal"
                else:
                    folder = "normal"
                pokemon_url_name = pokemon.replace(" ", "-")
                await ctx.send("https://img.pokemondb.net/sprites/home/" + folder +"/"+ pokemon_url_name.lower() +".png")



        with open(r"data/pokemon.json", "r") as read_file:
            data = json.load(read_file)
        pokemon = str((pkmn.lower()).title())
        possible_names = []
        for i in range(0, len(data)):
            pkmn_info = data[i]
            if pkmn_info['name'].startswith(pokemon):
                poke_name = pkmn_info['name']
                possible_names.append(poke_name)
        if len(possible_names) == 0:
            print("No match")
        else:
            pokemon = possible_names[0]

        for i in range(0, len(data)):
            pokemon_dict = data[i]
            if pokemon in (pokemon_dict.values()):
                if shiny:
                    if shiny[0] == "*" or shiny[0].lower() == "shiny":
                        folder = "shiny"
                    else:
                        folder = "normal"
                else:
                    folder = "normal"
                pokemon_url_name = pokemon.replace(" ", "-")
                await ctx.send("https://img.pokemondb.net/sprites/home/" + folder +"/"+ pokemon_url_name.lower() +".png")


    @commands.command()
    async def dyna(self, ctx, *, pokemon):
        with open(r"data/da_mons.json", encoding='utf-8') as da_mon_dict:
            data = json.load(da_mon_dict)
        pokemon = (pokemon.lower()).title()

        possible_names = []
        for i in range(0, len(data)):
            pkmn_info = data[i]
            if pkmn_info['name'].startswith(pokemon):
                poke_name = pkmn_info['name']
                possible_names.append(poke_name)
        if len(possible_names) == 0:
            print("No match")
            return
        else:
            pokemon = possible_names[0]

        for i in range(0, len(data)):
            pkmn_info = data[i]
            if pokemon in (pkmn_info.values()):
                ability = pkmn_info["Ability"]
                pokemon_name = pkmn_info["name"]
                attacks = '\n'.join(attack for attack in pkmn_info["Attacks"])

        embed = discord.Embed(title=pokemon_name)
        embed.add_field(name="Ability", value=ability, inline=False)
        embed.add_field(name="Attacks", value=attacks)
        await ctx.send(embed=embed)
    
    
    @commands.command(hidden=True)
    async def dynadd(self, ctx, *, info):
        info_split = info.split("\n")
        with open(r"data/da_mons.json", encoding='utf-8') as da_mon_dict:
            da_mon_dict = json.load(da_mon_dict)
        name = info_split[0]
        ability = info_split[2]
        attacks = [info_split[5]] + [info_split[6]] + [info_split[7]] + [info_split[8]]
        new_poke = {"name":name, "Ability":ability, "Attacks":attacks}
        da_mon_dict.append(new_poke)
        print(type(da_mon_dict))
        print(da_mon_dict)
        new_dict = da_mon_dict
        try:
            with open(r"data/da_mons.json", "w", encoding='utf-8') as da_mon_dict:
                json.dump(new_dict, da_mon_dict, indent=4, ensure_ascii=False)
            await ctx.send("added "+name) 
        except:
            print("something went wrong")


    @commands.command(name = 'dex', aliases = ['pokedex'])
    async def dex(self, ctx, pkmn, *form_input):
        ability_check = ['ability1', 'ability2', 'abilityH']
        egg_group_check = ['eggGroup1', 'eggGroup2']
        forms_check = ['Galar', 'Galarian', 'galar', 'galarian', 'Male', 'male', 'Female', 'female', 'M', 'm', 'F', 'f',
                       'Alolan', 'alolan', 'Gigantamax', 'Gmax', 'Mega', 'mega', 'MegaX', 'megax', 'MegaY', 'megay',
                       'Ice Rider', 'Ice', 'ice','Shadow Rider','Shadow','shadow', 'Hisuian', 'hisuian',
                       'Paldean', 'paldean', 'Paldean Fire', 'paldean fire', 'Paldean Water', 'paldean water']
        stat_changing_forms_name_first = ['Male', 'male', 'Female', 'female', 'M', 'm', 'F', 'f']
        stat_changing_forms_name_last = ['hisuian', 'Hisuian', 'galar', 'Galar', 'Galarian', 'galarian', 'Alolan',
                                         'Mega', 'MegaX', 'MegaY', 'Ice Rider',
                                         'Shadow Rider', 'ice', 'Ice', 'shadow', 'Shadow',
                                         'Paldean', 'paldean', 'Paldean Fire', 'paldean fire', 'PaldeanFire', 'paldeanfire',
                                         'Paldean Water', 'paldean water', 'PaldeanWater', 'paldeanwater']
        typing_check = ['type1', 'type2']
        with open(r"data/pokemon.json", "r") as read_file:
            data = json.load(read_file)
        pokemon = ""
        possible_names = []
        poke_dict_forms = []
        if pkmn.isdigit():
            for i in range(0, len(data)):
                pkmn_info = data[i]
                if pkmn_info['dexId'] == int(pkmn):
                    poke_name = pkmn_info['name']
                    possible_names.append(poke_name)
                    poke_dict_forms = pkmn_info["forms"]
                    
        else:
            pokemon = str((pkmn.lower()).title())
            for i in range(0, len(data)):
                pkmn_info = data[i]
                if pkmn_info['name'].startswith(pokemon):
                    poke_name = pkmn_info['name']
                    possible_names.append(poke_name)
                    poke_dict_forms = pkmn_info["forms"]
        
        if len(possible_names) == 0:
            print("No match")
        else:
            pokemon = possible_names[0]
        
        if len(poke_dict_forms) == 0:
            form = ""
        else:
            available_forms = []
            if form_input:
                form_input = list(form_input)
                for i in form_input:
                    if i in forms_check:
                        available_forms.append(i)

                if len(available_forms) == 0:
                    form = ""
                else:
                    form = available_forms[0]
                    if form == 'm' or form == 'M' or form == 'male':
                        form = 'Male'
                    elif form == 'f' or form == 'F' or form == 'female':
                        form = 'Female'
                    elif form == 'gmax' or form == 'Gmax':
                        form = 'Gigantamax'
                    elif form == 'megax':
                        form = 'MegaX'
                    elif form == 'megay':
                        form = 'MegaY'
                    elif form == 'mega':
                        form = 'Mega'
                    elif form == 'alolan':
                        form = 'Alolan'
                    elif form == 'ice' or form == 'Ice':
                        form = 'Ice Rider'
                    elif form == 'shadow' or form == 'Shadow':
                        form = 'Shadow Rider'
                    elif form in ['galar', 'galarian', 'Galar', 'Galarian']:
                        form = "Galarian"
                    elif form == "hisuian":
                        form = "Hisuian"
                    elif form in ['Paldean', 'paldean']:
                        form == 'Paldean'
                    elif form == "paldeanwater" or form == "PaldeanWater":
                        form == "Paldean Water"
                    elif form == "paldeanfire" or form == "PaldeanFire":
                        form == "Paldean Fire"
            else:
                form = ""

        if form in stat_changing_forms_name_first or form in stat_changing_forms_name_last:
            if form in stat_changing_forms_name_first:
                if form == 'Male':
                    pokemon_lookup = pokemon
                else:
                    pokemon_lookup = pokemon + " " + form
            elif form in stat_changing_forms_name_last:
                pokemon_lookup = form + " " + pokemon
        else:
            pokemon_lookup = pokemon

        for i in range(0, len(data)):
            pkmn_info = data[i]
            if pokemon_lookup in (pkmn_info.values()):
                abilities_dict = pkmn_info["abilities"]
                ability_list = [abilities_dict[ability] for ability in ability_check if abilities_dict[ability] is not None]
                poke_dict_forms = pkmn_info["forms"]
                pokemon_name = pkmn_info["name"]
                # Construction depending on 1, 2 or 3 abilities
                if len(ability_list) == 3:
                    ability_1 = "Ability 1: `" + ability_list[0] + "`\n"
                    ability_2 = "Ability 2: `" + ability_list[1] + "`\n"
                    ability_h = "Ability H: `" + ability_list[2] + "`"
                    ability = ability_1 + ability_2 + ability_h
                elif len(ability_list) == 2:
                    ability_1 = "Ability 1: `" + ability_list[0] + "`\n"
                    ability_h = "Ability H: `" + ability_list[1] + "`\n"
                    ability = ability_1 + ability_h
                else:
                    ability = "Ability 1: `" + ability_list[0] + "`\n"
                
                typing_list = [pkmn_info[typing] for typing in typing_check if pkmn_info[typing] is not None]
                # Adjust for single or dual type
                if len(typing_list) == 1:
                    typing = "Type: `" + typing_list[0] + "`"
                else:
                    typing = "Type: `" + typing_list[0] + "/" + typing_list[1] + "`"
                
                egg_groups = ', '.join([pkmn_info[group] for group in egg_group_check if pkmn_info[group] is not None])
                catch_rate = "Catch rate: `" + str(pkmn_info["catchRate"]) + "`"
                base_stats = pkmn_info["baseStats"]
                stats = ["hp", "atk", "def", "spA", "spD", "spe", "tot"]
                stat_value = [base_stats[stat] for stat in stats]

                dens = pkmn_info["dens"]
                sword_dens_list = dens["sword"]
                # sword_dens = ', '.join("["+str(sword_dens_list[i])+"]" + "(https://www.serebii.net/swordshield/maxraidbattles/den"+str(sword_dens_list[i])+".shtml)" for i in range(0, len(sword_dens_list)) if len(sword_dens_list) is not None)
                sword_dens = ', '.join(sword_dens_list[i] for i in range(0, len(sword_dens_list)) if len(sword_dens_list) is not None)
                shield_dens_list = dens["shield"]
                # shield_dens = ', '.join("["+str(shield_dens_list[i])+"]" + "(https://www.serebii.net/swordshield/maxraidbattles/den"+str(shield_dens_list[i])+".shtml)" for i in range(0, len(shield_dens_list)) if len(shield_dens_list) is not None)
                shield_dens = ', '.join(shield_dens_list[i] for i in range(0, len(shield_dens_list)) if len(shield_dens_list) is not None)
                pokemon_forms = []
                if len(poke_dict_forms) !=0:
                    for i in range(0, len(poke_dict_forms)):
                        if poke_dict_forms[i] in forms_check:
                            i = poke_dict_forms[i]
                            pokemon_forms.append(i)
                    if pokemon_forms == ['Male', 'Female', 'm', 'f']:
                        pokemon_forms.remove('m')
                        pokemon_forms.remove('f')

                    pokemon_forms = "Forms: `" + ', '.join(pokemon_forms[i] for i in range(0, len(pokemon_forms))) + "`"
                else:
                    pokemon_forms = ""

                if form != "":
                    if form == 'MegaX':
                        pokemon_name = "Mega " + pokemon + " X"
                    elif form == 'MegaY':
                        pokemon_name = "Mega " + pokemon + " Y"
                    else:
                        pokemon_name = pokemon_name

                if 'shiny' in form_input or '*' in form_input:
                    folder = "shiny"
                else:
                    folder = "normal"


                pokemon_url_name = pokemon.replace(" ", "-")

                embed = discord.Embed(title="__#" + str(pkmn_info["dexId"]) +  " " + pokemon_name + "__", colour=0xFF0000)
                embed.add_field(name="Misc. Info", value=typing + "\n" + catch_rate + "\nEgg Groups: `" + egg_groups + "`\n" + pokemon_forms)
                embed.add_field(name="Abilities", value=ability, inline=True)
                embed.add_field(
                    name="Base stats: ",
                    value="__`HP     Atk     Def`__\n"+""
                    "__`"+ f"{str(stat_value[0]):<7}" + f"{str(stat_value[1]):<8}" + f"{str(stat_value[2]):<3}" + "`__\n"
                    "__`SpA    SpD     Spe`__\n"
                    "__`"+ f"{str(stat_value[3]):<7}" + f"{str(stat_value[4]):<8}" + f"{str(stat_value[5]):<3}" +"`__\n"
                    "__`Total: " + str(stat_value[6]) + "`__")
                if len(sword_dens_list) != 0 or len(shield_dens_list) != 0:
                    embed.add_field(name="Dens", value="Sword: " + str(sword_dens) + "\nShield: " + str(shield_dens) + "", inline=False)
                
                if pokemon_lookup == 'Ice Rider Calyrex':
                    url = 'https://www.serebii.net/swordshield/pokemon/898-i.png'
                    embed.set_image(url=url)
                elif pokemon_lookup == 'Shadow Rider Calyrex':
                    url = 'https://www.serebii.net/swordshield/pokemon/898-s.png'
                    embed.set_image(url=url)
                else:
                    embed.set_image(url="https://img.pokemondb.net/sprites/home/" + folder +"/"+ pokemon_url_name.lower() + form + ".png")
            
                await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Dexter(client))

async def sendSprites(ctx, genderDifference, hasBackSprites, url, urlBack, urlFemale, urlFemaleBack):
    if requests.head(url).status_code == 200:
        if genderDifference:
            await ctx.send("This pokemon has gender differences!")
            await ctx.send("Male sprite:")
        await ctx.send(url)
        if hasBackSprites:
            await ctx.send(urlBack)
        if genderDifference:
            await ctx.send("Female sprite:")
            await ctx.send(urlFemale)
            if hasBackSprites:
                await ctx.send(urlFemaleBack)

def generatePictureUrl(name:str, shiny, genderDifference, generation):
    db = "home"
    folder = "shiny" if shiny else "normal"
    name = name.lower().replace(" ", "-")
    if name.lower().startswith("nidoran"):
        name = name.replace("female", "f")
        if not name.lower().endswith("f"):
            name = name + "-m"
    url = f"https://img.pokemondb.net/sprites/{db}/{folder}/{name}.png"
    urlBack = f"https://img.pokemondb.net/sprites/{db}/back-{folder}/{name}.png"
    urlFemale = None
    urlFemaleBack = None
    if genderDifference:
        urlFemale = f"https://img.pokemondb.net/sprites/{db}/{folder}/{name}-f.png"
        urlFemaleBack = f"https://img.pokemondb.net/sprites/{db}/back-{folder}/{name}-f.png"
    return url, urlBack, urlFemale, urlFemaleBack

def correctForDarmanitan(pkmn, form):
    if not form:
        form = ""
    pkmn = pkmn + " " + form
    pkmn = pkmn.lower()
    darmanitanNameAndForm = None
    if "darmanitan" in pkmn:
        darmanitanNameAndForm = "darmanitan"
        if "galarian" in pkmn:
            darmanitanNameAndForm = darmanitanNameAndForm + "-galarian"
        if "zen" in pkmn:
            darmanitanNameAndForm = darmanitanNameAndForm + "-zen"
        else:
            darmanitanNameAndForm = darmanitanNameAndForm + "-standard"
    return darmanitanNameAndForm

def pokemonLookUp(pkmn:str, form:str):
    pokemonName = None
    darmanitan = correctForDarmanitan(pkmn, form)
    if darmanitan:
        pokemonName = darmanitan
    with open(r"data/pokemon.json", "r") as readFile:
        data = json.load(readFile)
    if not darmanitan:
        for i in range(0, len(data)):
            pkmnInfo = data[i]
            if pkmnInfo['name'].lower().startswith(pkmn):
                if form and hasRequestedForm(form, pkmnInfo['forms']):
                    pokemonName = pkmnInfo['name'] + "-" + form
                else:
                    pokemonName = pkmnInfo['name']
                break
    for i in range(0, len(data)):
        pkmnInfo = data[i]
        if pkmnInfo['name'].lower() == pokemonName.lower():
            return pkmnInfo

def hasRequestedForm(formRequested, formsAvailable):
    for i in formsAvailable:
        if formRequested.lower() in i.lower():
            return True
    return False

def checkIfShinySpriteRequest(pkmn:str):
    if "*" in pkmn or "shiny" in pkmn:
        return True
    return False

async def hasGenderDifference(dexId):
    statusCode, pokemonResult = await fetchPokemonSpecies(dexId)
    if pokemonResult and pokemonResult["has_gender_differences"]:
        return pokemonResult["has_gender_differences"]
    return False

def checkIfFormRequested(pkmn:str):
    pokemonForms = regionForms + rotomForms + genderForms + temporaryForms + calyrexForms
    wordList = pkmn.split(" ")
    for form in pokemonForms:
        for word in wordList:
            if word in form and len(word)>2:
                return form, word
    return None, None
