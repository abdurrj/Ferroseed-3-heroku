from BotImports import *

async def fetchPokemon(pokemon):
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")
    print(r.status_code)
    if r.status_code == 200:
        return r.status_code, r.json()
    else:
        return r.status_code, None

async def fetchPokemonSpecies(pokemon):
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/pokemon-species/{pokemon}")
    if r.status_code == 200:
        return r.status_code, r.json()
    else:
        return r.status_code, None

async def fetchAbility(ability):
    r = requests.get(f"https://pokeapi.co/api/v2/ability/{ability}").json()
    if r.status_code == 200:
        return r.status_code, r.json()
    else:
        return r.status_code, None