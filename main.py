import os
from discord import Client
from discord import Message
from discord import TextChannel
from discord import User
import requests
import json
from replit import db
from cards import Deck

client = Client()
deck = Deck()

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

async def deal_hand(user: User):
  hand = []
  hand.append(deck.take_random_card_from_deck())
  hand.append(deck.take_random_card_from_deck())
  hand.append(deck.take_random_card_from_deck())
  await user.send('Your hand: ' + str(hand[0]) + ' & ' + str(hand[1]) + ' & ' + str(hand[2]))

async def send_message(message: Message):
  global deck
  if message.author == client.user:
    return

  if message.content.startswith('$deal_hand') and isinstance(message.channel, TextChannel):
    store_channel(message.channel)
    await deal_hand(message.author)
    await message.channel.send('Dealt you a hand. Check your DM. Number of cards remaining in deck: ' + str(deck.number_of_cards_remaining()))
  elif message.content.startswith('$deal_hand') and not isinstance(message.channel, TextChannel):
    await message.channel.send('Cannot deal hand from DM.')

  if message.content.startswith('$reshuffle_deck') and isinstance(message.channel, TextChannel):
    deck = Deck()
    await message.channel.send('Deck has been reshuffled')

  if message.content.startswith('$inspire'):
    quote = get_quote()
    await message.author.send(quote)

def store_channel(channel: TextChannel):
  db["channel"] = channel.id

def retrieve_channel():
  return client.get_channel(db["channel"])

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message: Message):
  await send_message(message)

@client.event
async def on_message_edit(before: Message, after: Message):
  if before.content != after.content:
    await send_message(after)

client.run(os.getenv('TOKEN'))
