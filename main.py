import os
from discord import Client
from discord import Embed
from discord import Message
from discord import DMChannel
from discord import TextChannel
from game import Game
from keep_alive import keep_alive
from util import Util

client = Client()
games = {}

async def determine_channel_id(message: Message):
  if isinstance(message.channel, DMChannel):
    ### First see if a message is being referenced
    if message.reference is not None:
      references_message = await message.channel.fetch_message(message.reference.message_id)
      if references_message.author == client.user and len(references_message.embeds) > 0 and references_message.embeds[0].footer.text is not Embed.Empty:
        channel_id = int(references_message.embeds[0].footer.text)
        return channel_id
    ### If not message is referenced use DM history
    for message in await message.channel.history(limit=200).flatten():
      if message.author == client.user and len(message.embeds) > 0 and message.embeds[0].footer.text is not Embed.Empty:
        channel_id = int(message.embeds[0].footer.text)
        return channel_id
  else:
    return message.channel.id

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message: Message):
  channel_id = await determine_channel_id(message)

  if isinstance(message.channel, DMChannel) and channel_id not in games:
    print(f'Game for channel ID `{channel_id}` could not be found')
    await Util.send_error_embed(message.channel, 'Could not find a game.')
    return
  elif isinstance(message.channel, TextChannel) and channel_id not in games:
    print(f'Creating new game for `#{message.channel}` ({channel_id}) on {message.guild}')
    games[channel_id] = Game(client, message.channel)

  await games[channel_id].send_message(message)

@client.event
async def on_message_edit(before: Message, after: Message):
  if before.content != after.content:
    channel_id = await determine_channel_id(after)
    await games[channel_id].send_message(after)

keep_alive()
client.run(os.getenv('TOKEN'))
