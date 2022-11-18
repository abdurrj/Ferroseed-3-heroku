from modules.PokeApiConsumer import *
from BotImports import *

ABILITIES = "abilities"
NAME = "name"
POKEDEX_NUMBER = "id"
STATS = "stats"

class AdvancedDex(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def lookUpPokemon(self, ctx, *, pokemon):
        httpResult, pokemonResult = await fetchPokemon(pokemon)
        if httpResult != 200:
            await ctx.send(f"Sorry, i couldn't find {pokemon}")
            return

        # print(pokemonResult)
        processPokemonResult(pokemonResult)

        await ctx.send("Pokemon found. processing")

    @commands.command()
    async def lookUpAbility(self, ctx, *, ability):
        await fetchAbility(ability)



def setup(client):
    client.add_cog(AdvancedDex(client))

def processPokemonResult(pokeInfo):
    pokemonName = pokeInfo[NAME]
    pokemonAbilities = pokeInfo[ABILITIES]
    pokemonDexNumber = pokeInfo[POKEDEX_NUMBER]
    pokemonStatsDict = processBaseStats(pokeInfo[STATS])


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