import discord
from typing import List
from config import client
from datetime import datetime
import pytz

# List to keep track of events
events = []

# Time zone
CT = pytz.timezone('US/Central')

class PollButtons(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.yes_votes: List[int] = []
        self.no_votes: List[int] = []

    @discord.ui.button(label="👍 Yes", style=discord.ButtonStyle.green)
    async def thumbs_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.yes_votes:
            self.yes_votes.append(interaction.user.id)
            if interaction.user.id in self.no_votes:
                self.no_votes.remove(interaction.user.id)
            await self.update_poll_message(interaction)

    @discord.ui.button(label="👎 No", style=discord.ButtonStyle.danger)
    async def thumbs_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.no_votes:
            self.no_votes.append(interaction.user.id)
            if interaction.user.id in self.yes_votes:
                self.yes_votes.remove(interaction.user.id)
            await self.update_poll_message(interaction)

    async def update_poll_message(self, interaction: discord.Interaction):
        yes_votes = ', '.join([f"<@{user_id}>" for user_id in self.yes_votes]) or "None"
        no_votes = ', '.join([f"<@{user_id}>" for user_id in self.no_votes]) or "None"

        updated_embed = discord.Embed(
            title=self.message.embeds[0].title,
            description=self.message.embeds[0].description
        )
        updated_embed.add_field(name="👍 Yes", value=yes_votes, inline=False)
        updated_embed.add_field(name="👎 No", value=no_votes, inline=False)

        await self.message.edit(embed=updated_embed)
        await interaction.response.send_message("Your vote has been counted.", ephemeral=True)

        for event in events:
            if event[1] == interaction.channel.id and event[2] == self.message.embeds[0].description.split('\n\n')[0]:
                event[5] = self.yes_votes

class PollModal(discord.ui.Modal, title="Create Poll"):
    poll_message = discord.ui.TextInput(label="Poll Title", style=discord.TextStyle.paragraph, max_length=200)
    date = discord.ui.TextInput(label="Date (YYYY-MM-DD)", style=discord.TextStyle.short)
    time = discord.ui.TextInput(label="Time (HH:MM)", style=discord.TextStyle.short)

    def __init__(self, *args, poll_message_value="", date_value="", time_value="", error_message="", **kwargs):
        super().__init__(*args, **kwargs)
        self.poll_message.default = poll_message_value
        self.date.default = date_value
        self.time.default = time_value
        self.error_message = error_message

    async def on_submit(self, interaction: discord.Interaction):
        try:
            play_date = datetime.strptime(self.date.value, '%Y-%m-%d')
            play_time = datetime.strptime(self.time.value, '%H:%M')
            combined_datetime = datetime.combine(play_date, play_time.time())
            combined_datetime = CT.localize(combined_datetime)
            utc_datetime = combined_datetime.astimezone(pytz.utc)
        except ValueError:
            modal = PollModal(
                poll_message_value=self.poll_message.value,
                date_value=self.date.value,
                time_value=self.time.value,
                error_message="Invalid date/time format. Please use 'YYYY-MM-DD' for the date and 'HH:MM' for the time."
            )
            await interaction.response.send_modal(modal)
            return

        emb = discord.Embed(
            title="EVENT/POLL",
            description=f"{self.poll_message.value}\n\n**Proposed Time (CT):** {combined_datetime.strftime('%Y-%m-%d %H:%M %Z')}"
        )
        poll_message = await interaction.channel.send(embed=emb)
        view = PollButtons(poll_message)
        await poll_message.edit(view=view)

        events.append([utc_datetime, interaction.channel.id, self.poll_message.value, False, False, []])
        print(f"Event scheduled: {self.poll_message.value} at {utc_datetime} (UTC) / {combined_datetime} (CT)")
        await interaction.response.send_message("Poll created successfully.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, discord.ext.commands.CommandError):
            await interaction.response.send_modal(self)

class CreatePollButton(discord.ui.View):
    @discord.ui.button(label="Create Poll", style=discord.ButtonStyle.primary)
    async def create_poll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PollModal()
        await interaction.response.send_modal(modal)

# Poll command
@client.command()
async def createpoll(ctx):
    view = CreatePollButton()
    await ctx.send("Click the button below to create a poll.", view=view)

# Command to cancel an event
@client.command()
async def cancelpoll(ctx, *, event_name: str):
    global events
    for event in events:
        if event[2] == event_name and event[1] == ctx.channel.id:
            events.remove(event)
            await ctx.send(f"Event '{event_name}' has been canceled.")
            print(f"Event '{event_name}' has been canceled.")
            return
    await ctx.send(f"No event found with the name '{event_name}' in this channel.")
    print(f"No event found with the name '{event_name}' in this channel.")
