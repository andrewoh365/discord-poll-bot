from discord.ext import commands
from config import client
from tasks import check_events

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    check_events.start()  # Start the background task to check events

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)
