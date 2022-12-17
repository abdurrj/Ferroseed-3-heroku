from modules.PokeApiConsumer import *

ABILITIES = "abilities"
NAME = "name"
POKEDEX_NUMBER = "id"
STATS = "stats"

regionForms = ["alolan", "galarian", "hisuian", "paldean", "paldean-fire", "paldean-water"]
rotomForms = ["fan", "frost", "heat", "mow", "wash"]
genderForms = ["male", "female", "f", "m"]
temporaryForms = ["mega", "mega-x", "mega-y", "gigantamax"]

class AdvancedDex(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def lookUpPokemon(self, ctx, *, pokemon):
        httpResult, pokemonResult = await fetchPokemon(pokemon)
        if httpResult != 200:
            httpResult, pokemonResult = await fetchPokemon(pokemon+"-m")
            if httpResult != 200:
                await ctx.send(f"Sorry, i couldn't find {pokemon}")
                return

        # print(pokemonResult)
        processPokemonResult(pokemonResult)

        await ctx.send("Pokemon found. processing")

    @commands.command()
    async def lookUpAbility(self, ctx, *, ability):
        await fetchAbility(ability)

    @commands.command()
    async def namecons(self, ctx, *, pkmn:str):
        pkmn = pkmn.lower()
        isShiny = checkIfShinySpriteRequest(pkmn)
        formFound, formRequested = checkIfFormRequested(pkmn)
        if formFound:
            pkmn = pkmn.replace(formRequested, "").strip()
        if isShiny:
            pkmn = pkmn.replace("shiny", "").replace("*", "").strip()

        pokemonData = pokemonLookUp(pkmn, formFound)
        if formFound and formFound not in pokemonData['name']:
            return
        genderDifference = await hasGenderDifference(pokemonData["dexId"])
        url, urlBack, urlFemale, urlFemaleBack = generatePictureUrl(pokemonData["name"], isShiny, genderDifference)
        hasBackSprites = requests.head(urlBack).status_code == 200
        await ctx.send(url)
        if hasBackSprites:
            await ctx.send(urlBack)
        if genderDifference:
            await ctx.send("Female sprite")
            await ctx.send(urlFemale)
            if hasBackSprites:
                await ctx.send(urlFemaleBack)

def setup(client):
    client.add_cog(AdvancedDex(client))

def generatePictureUrl(name:str, shiny, genderDifference):
    folder = "shiny" if shiny else "normal"
    name = name.lower()
    url = f"https://img.pokemondb.net/sprites/home/{folder}/{name}.png"
    urlBack = f"https://img.pokemondb.net/sprites/home/back-{folder}/{name}.png"
    urlFemale = None
    urlFemaleBack = None
    if genderDifference:
        urlFemale = f"https://img.pokemondb.net/sprites/home/{folder}/{name}-f.png"
        urlFemaleBack = f"https://img.pokemondb.net/sprites/home/back-{folder}/{name}-f.png"
    return url, urlBack, urlFemale, urlFemaleBack

def pokemonLookUp(pkmn:str, form:str):
    pokemonName = None
    with open(r"data/pokemon.json", "r") as readFile:
        data = json.load(readFile)
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
        if pkmnInfo['name'] == pokemonName:
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
    pokemonForms = regionForms + rotomForms + genderForms + temporaryForms
    wordList = pkmn.split(" ")
    for form in pokemonForms:
        for word in wordList:
            if word in form and len(word)>2:
                if form == "male":
                    form = ""
                elif form == "female":
                    form = "f"
                return form, word
    return None, None

def processPokemonResult(pokeInfo):
    pokemonName = pokeInfo[NAME]
    pokemonAbilities = getPokemonAbilitiesAsString(pokeInfo[ABILITIES])
    print(pokemonAbilities)
    pokemonDexNumber = pokeInfo[POKEDEX_NUMBER]
    pokemonStatsDict = processBaseStats(pokeInfo[STATS])


def getPokemonAbilitiesAsString(abilityList):
    abilities = ""
    for i in abilityList:
        abilityName = i["ability"]["name"]
        if i["is_hidden"]:
            abilitySlot = "H"
        else:
            abilitySlot = i["slot"]
        abilities = abilities + f"Ability {abilitySlot}: `{abilityName}`"
        if not abilityList.index(i) == len(abilityList)-1:
            abilities = abilities + "\n"

    return abilities


def processBaseStats(pokemonBaseStats):
    stats = {}
    stats["hp"] = pokemonBaseStats[0]["base_stat"]
    stats["atk"] = pokemonBaseStats[1]["base_stat"]
    stats["def"] = pokemonBaseStats[2]["base_stat"]
    stats["spA"] = pokemonBaseStats[3]["base_stat"]
    stats["spD"] = pokemonBaseStats[4]["base_stat"]
    stats["spe"] = pokemonBaseStats[5]["base_stat"]
    stats["tot"] = calculateTotalStats(stats)
    return stats

def calculateTotalStats(stats):
    totalStats = 0
    for stat in stats.keys():
        totalStats += stats[stat]

    return totalStats