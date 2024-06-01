import discord
from typing import Final, List
import os
from discord.ext import commands
from dotenv import load_dotenv
from discord import Intents, Message
from responses import get_response

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='.', intents=intents)

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    is_private = user_message[0] == '?'
    user_message = user_message[1:] if is_private else user_message

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')

# Define the buttons and voting logic
class PollButtons(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.yes_votes: List[str] = []
        self.no_votes: List[str] = []

    @discord.ui.button(label="👍", style=discord.ButtonStyle.green)
    async def thumbs_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name not in self.yes_votes:
            self.yes_votes.append(interaction.user.name)
            if interaction.user.name in self.no_votes:
                self.no_votes.remove(interaction.user.name)
            await self.update_poll_message(interaction)

    @discord.ui.button(label="👎", style=discord.ButtonStyle.red)
    async def thumbs_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name not in self.no_votes:
            self.no_votes.append(interaction.user.name)
            if interaction.user.name in self.yes_votes:
                self.yes_votes.remove(interaction.user.name)
            await self.update_poll_message(interaction)

    async def update_poll_message(self, interaction: discord.Interaction):
        yes_votes = ', '.join(self.yes_votes) or "None"
        no_votes = ', '.join(self.no_votes) or "None"

        updated_embed = discord.Embed(
            title=self.message.embeds[0].title,
            description=self.message.embeds[0].description
        )
        updated_embed.add_field(name="Yes", value=yes_votes, inline=False)
        updated_embed.add_field(name="No", value=no_votes, inline=False)

        await self.message.edit(embed=updated_embed)
        await interaction.response.send_message("Your vote has been counted.", ephemeral=True)

# From Poll Tutorial
@client.command()
async def poll(ctx, *, message):
    if not message:
        await ctx.send("Poll message cannot be empty.")
        return
    emb = discord.Embed(title="POLL", description=f"{message}")
    poll_message = await ctx.send(embed=emb)
    view = PollButtons(poll_message)
    await poll_message.edit(view=view)

# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = str(message.content)
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: {user_message}')
    await send_message(message, user_message)
    await client.process_commands(message)

# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()
