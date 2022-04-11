from BotImports import *

intents = discord.Intents.all()

client = commands.Bot(
    command_prefix=(getPrefix),
    intents = intents
)

@client.event
async def on_ready():
    loadedModuleList = []
    failedModuleList = []
    print(f"logged in as {client.user.name}\nID: {client.user.id}")
    print("\n--------\nLoading modules")
    modules = getExternalModules()
    for i in modules:
        try:
            client.load_extension('modules.'+i)
            loadedModuleList.append(i)
        except ValueError as error:
            print(f"Could not load module {i}")
            print(f"{i}: {error}")
            failedModuleList.append(i)
    # client.load_extension('RaidCommands')
    
    print("Loaded modules: "+ ', '.join(i for i in loadedModuleList))
    print("Modules not loaded: "+ ', '.join(i for i in failedModuleList))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        await client.process_commands(message)

@client.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    await ctx.send(f"Command registered, latency: {str(round(client.latency, 4))}")

client.run(TOKEN)