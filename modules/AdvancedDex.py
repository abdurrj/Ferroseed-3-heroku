from modules.PokeApiConsumer import *

ABILITIES = "abilities"
NAME = "name"
POKEDEX_NUMBER = "id"
STATS = "stats"

regionForms = ["alolan", "galarian", "hisuian", "paldean"]
rotomForms = ["fan", "frost", "heat", "mow", "wash"]
genderForms = ["male", "female"]
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

        print(pkmn)
        pokemonFromData = pokemonLookUp(pkmn, formFound)
        print(pokemonFromData)

def setup(client):
    client.add_cog(AdvancedDex(client))

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
    return pokemonName

def hasRequestedForm(formRequested, formsAvailable):
    for i in formsAvailable:
        if formRequested.lower() in i.lower():
            return True
    return False

def checkIfShinySpriteRequest(pkmn:str):
    if "*" in pkmn or "shiny" in pkmn:
        return True
    return False

def checkIfFormRequested(pkmn:str):
    pokemonForms = regionForms + rotomForms + genderForms + temporaryForms
    wordList = pkmn.split(" ")
    for form in pokemonForms:
        for word in wordList:
            if word in form and len(word)>2:
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