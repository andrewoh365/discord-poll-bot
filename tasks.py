from discord.ext import tasks
from config import client
from datetime import datetime, timedelta
import pytz
from poll import events

@tasks.loop(seconds=30)
async def check_events():
    if not events:
        return

    now = datetime.now(pytz.utc)
    print(f"Checking events at {now}")
    for event in events:
        event_time, channel_id, event_name, reminder_sent, start_notified, participants = event
        time_until_event = (event_time - now).total_seconds()
        print(f"Event '{event_name}' scheduled for {event_time} (UTC), which is in {time_until_event / 60:.2f} minutes.")
        
        if not reminder_sent and timedelta(minutes=10, seconds=-15) <= event_time - now <= timedelta(minutes=10, seconds=15):
            channel = client.get_channel(channel_id)
            if channel:
                mentions = ' '.join([f"<@{user_id}>" for user_id in participants])
                print(f"Sending reminder for event: {event_name} in channel {channel_id}")
                await channel.send(f"Reminder: Event '{event_name}' is happening in 10 minutes! {mentions}")
                event[3] = True
            else:
                print(f"Channel {channel_id} not found.")
        
        if not start_notified and timedelta(seconds=-15) <= event_time - now <= timedelta(seconds=15):
            channel = client.get_channel(channel_id)
            if channel:
                mentions = ' '.join([f"<@{user_id}>" for user_id in participants])
                print(f"Sending event start notification for event: {event_name} in channel {channel_id}")
                await channel.send(f"The event '{event_name}' is starting now! {mentions}")
                event[4] = True
            else:
                print(f"Channel {channel_id} not found.")
    
    events[:] = [event for event in events if event[0] > now]
