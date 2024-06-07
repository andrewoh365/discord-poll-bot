import discord
from discord.ext import commands, tasks
from discord import Intents
from config import TOKEN
from events import check_events
from poll import PollModal

# STEP 1: BOT SETUP
intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='.', intents=intents)

# STEP 2: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')
    check_events_task.start()  # Start the background task to check events

class CreatePollButton(discord.ui.View):
    @discord.ui.button(label="Create Poll", style=discord.ButtonStyle.primary)
    async def create_poll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PollModal()
        await interaction.response.send_modal(modal)

# From Poll Tutorial
@client.command()
async def createpoll(ctx):
    view = CreatePollButton()
    await ctx.send("Click the button below to create a poll.", view=view)

# Command to cancel an event
@client.command()
async def cancelpoll(ctx, *, event_name: str):
    from events import events
    # Find the event by name and remove it
    for event in events:
        if event[2] == event_name and event[1] == ctx.channel.id:
            events.remove(event)
            await ctx.send(f"Event '{event_name}' has been canceled.")
            print(f"Event '{event_name}' has been canceled.")
            return
    await ctx.send(f"No event found with the name '{event_name}' in this channel.")
    print(f"No event found with the name '{event_name}' in this channel.")

# Background task to check events
@tasks.loop(seconds=30)
async def check_events_task():
    await check_events(client)

# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return

    await client.process_commands(message)

# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()
