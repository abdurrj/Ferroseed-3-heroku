from numpy import outer
from BotImports import *


#######################################################################################

reactrole_path = 'main/data/reactrole.json'

async def readReactionRolesFromDb(client, guild_id):
    reactionRoleResponse = await client.db.fetch('SELECT reaction_role_map from ferroseed.reaction_roles WHERE guild_id = $1', guild_id)
    if len(reactionRoleResponse) == 0:
        guild_dict = {}
        await writeReactionRolesToDb(client, guild_id, guild_dict)
    else:
        guild_dict = ast.literal_eval(reactionRoleResponse[0].get("reaction_role_map"))
        if type(guild_dict)=='tuple':
            guild_dict = guild_dict[0]
    return guild_dict

async def writeReactionRolesToDb(client, guild_id, guild_dict):
    await client.db.execute('UPDATE ferroseed.reaction_roles SET reaction_role_map=$1 WHERE guild_id=$2', replaceQuotesOnString(str(guild_dict)), guild_id)

def replaceQuotesOnString(inputString):
    output = inputString.replace("'", '"')
    return output

class reactrole(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener("on_raw_reaction_add")
    async def give_role(self, payload):
        guild_id = payload.guild_id
        guild = self.client.get_guild(guild_id)
        channel_id = payload.channel_id
        guild_dict = await readReactionRolesFromDb(self.client, guild_id)
        if str(channel_id) in guild_dict.keys():
            message_dict = guild_dict[str(channel_id)]
            if str(payload.message_id) in message_dict.keys():
                react_dict = message_dict[str(payload.message_id)]
                if payload.emoji.name in react_dict.keys():
                    role_id = react_dict[payload.emoji.name]
                    role = discord.utils.get(guild.roles, id=int(role_id))
                    if role:
                        member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                        if member and member!=self.client.user:
                            await member.add_roles(role)
                            print(f"Added {role} to {member}")
                        else:
                            print("member not found or member = bot")
                    else:
                        print("role not found")

    
    @commands.Cog.listener("on_raw_reaction_remove")
    async def role_remove(self, payload):
        guild_id = payload.guild_id
        guild = self.client.get_guild(guild_id)
        channel_id = payload.channel_id
        guild_dict = await readReactionRolesFromDb(self.client, guild_id)
        if str(channel_id) in guild_dict.keys():
            message_dict = guild_dict[str(channel_id)]
            if str(payload.message_id) in message_dict.keys():
                react_dict = message_dict[str(payload.message_id)]
                if payload.emoji.name in react_dict.keys():
                    role_id = react_dict[payload.emoji.name]
                    role = discord.utils.get(guild.roles, id=int(role_id))
                    if role:
                        member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                        if member and member!=self.client.user:
                            await member.remove_roles(role)
                            print(f"removed {role} from {member}")
                        else:
                            print("member not found")
                    else:
                        print("role not found")
       
    
    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def register_role(self, ctx, reaction, role:discord.Role, message:discord.Message):
        guild_id = ctx.guild.id
        guild_dict = await readReactionRolesFromDb(self.client, guild_id)
        
        if not message:
            message = self.temp_message
            if not message:
                await ctx.send("Please specify a message by adding message URL, message ID, or by setting a temporary message with `set_message` command.")
                return

        if reaction.startswith('<'):
            reaction_name =  re.findall(r":([^:]*):", reaction)
            reaction_name = reaction_name[0]
        else:
            reaction_name = reaction
        if str(guild_id) in list(guild_dict.keys()):
            channel_dict = guild_dict[f"{guild_id}"]
        else:
            channel_dict = {}
        if str(message.channel.id) in list(channel_dict.keys()):
            message_dict = channel_dict[f"{message.channel.id}"]
        else:
            message_dict = {}
        if str(message.id) in list(message_dict.keys()):
            react_role_dict = message_dict[f"{message.id}"]
        else:
            react_role_dict = {}
        
        allowed_mentions = AllowedMentions(roles=False)
        if str(reaction_name) in list(react_role_dict.keys()):
            registered_role = ctx.guild.get_role(int(react_role_dict[f"{reaction_name}"]))
            await ctx.send(f"Emoji {reaction} already registered to {registered_role.mention}", allowed_mentions=allowed_mentions)
            return
        elif str(role.id) in list(react_role_dict.values()):
            await ctx.send(f"{role.mention} already registered to {reaction}", allowed_mentions=allowed_mentions)
            return
        else:
            react_role_dict[f"{reaction_name}"] = f"{role.id}"
            message_dict[f"{message.id}"] = react_role_dict
            channel_dict[f"{message.channel.id}"] = message_dict
            guild_dict[f"{guild_id}"] = channel_dict
            response = await writeReactionRolesToDb(self.client, guild_id, guild_dict)
            if response != "UPDATE 1":
                await ctx.send("Something went wrong")
                return
        await ctx.send(f"{role.mention} has been registered to {reaction} on message:\n{message.jump_url}", allowed_mentions=allowed_mentions)
        question = await ctx.send("Would you like me to react to that message with the specified emoji?")
        emoji_list = ['✅','❌']
        for i in emoji_list:
            await question.add_reaction(i)

        def checker(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emoji_list
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                r, user = await self.client.wait_for("reaction_add", timeout=15, check=checker)

                if str(r.emoji) == "✅":
                    await message.add_reaction(reaction)
                    await question.delete()
                    await ctx.send("Added reaction")
                    break

                elif str(r.emoji) == "❌":
                    await question.delete()
                    await ctx.send("Reaction not added")
                    break
            except asyncio.TimeoutError:
                break

            
    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def unregister_role(self, ctx, reaction, role:discord.Role, message:discord.Message=None):
        guild_id = ctx.guild.id
        guild_dict = await readReactionRolesFromDb(self.client, guild_id)
        if not message:
            message=self.temp_message
            if not message:
                await ctx.send("Please specify a message by adding message URL, message ID, or by setting a temporary message with `set_message` command.")
                return

        if reaction.startswith('<'):
            reaction_name = re.findall(r":([^:]*):", reaction)
            reaction_name = reaction_name[0]
        else:
            reaction_name = reaction
        channel_dict = guild_dict[str(guild_id)]
        message_dict = channel_dict[str(message.channel.id)]
        react_role_dict = message_dict[str(message.id)]
        allowed_mentions = AllowedMentions(roles=False)
        del react_role_dict[reaction_name]
        message_dict[f"{message.id}"] = react_role_dict
        channel_dict[f"{message.channel.id}"] = message_dict
        guild_dict[f"{guild_id}"] = channel_dict
        response = await writeReactionRolesToDb(self.client, guild_id, guild_dict)
        if response != "UPDATE 1":
            await ctx.send("Something went wrong")
            return
        await ctx.send(f"Removed {reaction} and {role} connection in the database", allowed_mentions=allowed_mentions)


def setup(client):
    client.add_cog(reactrole(client))