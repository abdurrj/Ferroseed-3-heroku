from BotImports import *

intents = discord.Intents.all()

client = commands.Bot(
    command_prefix=(getPrefix),
    intents = intents
)

async def create_db_pool():
    client.db = await asyncpg.create_pool(dsn=DATABASE_URL)
    print("connection is successfull")

async def main():
    await create_db_pool()
    await client.start(TOKEN)

def ext_modules_open():
    with open('data/ext_modules.json') as f:
        modules = json.load(f)
        return modules

@client.event
async def on_ready():
    loadedModuleList = []
    failedModuleList = []
    print(f"logged in as {client.user.name}\nID: {client.user.id}")
    print("\n--------\nLoading modules")
    if PROFILE == "prod":
        modules = await getExternalModules(client)
    else:
        modules = ext_modules_open()
    for i in modules:
        try:
            await client.load_extension('modules.'+i)
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

@client.event
async def on_thread_create(thread):
    await thread.join()
    await thread.send("<a:ferropeek:755450581774106706>")

@client.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    await ctx.send(f"Command registered, latency: {str(round(client.latency, 4))}")

asyncio.run(main())