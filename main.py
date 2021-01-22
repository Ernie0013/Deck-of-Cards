import os
import re
from discord import Client
from discord import Embed 
from discord import Message
from discord import DMChannel
from discord import Guild
from discord import Member
from discord import TextChannel
from discord import User
from replit import db
from cards import Deck
from keep_alive import keep_alive

client = Client()
deck = Deck()
dealt_hands = {}
prefix = '$'

def get_hand_embed(user: User, hand: []):
  cardDict = {
    "title": user.display_name + "'s Hand",
    "type": "rich",
    "description": get_hand_string(hand),
    "color": 16711680 if hand is None or len(hand) == 0 else 32768
  }
  return Embed.from_dict(cardDict)

def get_user_hand(user: User):
  global dealt_hands
  if user.id in dealt_hands:
    return dealt_hands[user.id]
  else:
    return None

def get_hand_string(hand: []):
  handString = ''
  if hand is None or len(hand) == 0:
    handString = 'No cards in hand'
  else:
    for card in hand:
      handString = handString + str(card) + '\n'
  return handString

async def send_hand_to_user(user: User):
  await user.send(embed = get_hand_embed(user, get_user_hand(user)))

def deal_hand(user: User, numberOfCards: int):
  hand = []
  for i in range(numberOfCards):
    card = deck.take_random_card_from_deck()
    hand.append(card)
  dealt_hands[user.id] = hand

def get_dealer_role(guild: Guild):
  return guild.get_role(db['dealer_role'])

def check_dealer_role(member: Member):
  return get_dealer_role(member.guild) in member.roles

async def send_message(message: Message):
  global deck
  global dealt_hands
  global prefix
  if message.author == client.user:
    return

  if message.content.startswith(prefix + 'prefix') and message.author.guild_permissions.administrator and isinstance(message.channel, TextChannel):
    prefixText = re.search(rf'{re.escape(prefix)}prefix (\S+)', message.content)
    if prefixText is not None and prefixText.group(1) is not None:
      prefix = prefixText.group(1)
      await message.channel.send('Prefix has been changed to `' + prefix + '`')
    else:
      await message.channel.send('Prefix is `' + prefix + '`')

  if message.content.startswith(prefix + 'dealer-role') and isinstance(message.channel, TextChannel):
    if message.role_mentions is not None and len(message.role_mentions) > 0:
      if message.author.guild_permissions.administrator:
        db['dealer_role'] = message.role_mentions[0].id
      else:
        await message.channel.send('Administrator privledges required to change dealer role')
    await message.channel.send('**' + str(get_dealer_role(message.guild)) + '** role is the dealer role')

  if message.content.startswith(prefix + 'deal-hand') and isinstance(message.channel, TextChannel): 
    if not check_dealer_role(message.author):
      await send_error_embed(message.channel, 'You are not the dealer')
      return
    store_channel(message.channel)
    numberText = re.search(rf'{re.escape(prefix)}deal-hand (\d+)', message.content)
    number = 2
    if numberText is not None and numberText.group(1) is not None:
      number = int(numberText.group(1))
    if number > deck.number_of_cards_remaining():
      await send_error_embed(message.channel, 'Not enough cards left in deck to deal hand')
      return
    deal_hand(message.author, number)
    await send_hand_to_user(message.author)
    await message.channel.send('Dealt you a hand. Check your DM. Number of cards remaining in deck: ' + str(deck.number_of_cards_remaining()))
  elif message.content.startswith(prefix + 'deal-hand') and not isinstance(message.channel, TextChannel):
    await message.channel.send('Cannot deal hand from DM.')

  if message.content.startswith(prefix + 'add-deck') and isinstance(message.channel, TextChannel):
    if not check_dealer_role(message.author):
      await send_error_embed(message.channel, 'You are not the dealer')
      return
    deck.add_deck()
    await message.channel.send('Deck added. Number of cards in deck: ' + str(deck.number_of_cards_remaining()))

  if message.content.startswith(prefix + 'show-hand') and isinstance(message.channel, DMChannel):
    returnChannel = retrieve_channel()
    await returnChannel.send(embed = get_hand_embed(message.author, get_user_hand(message.author)))
    await message.channel.send('Your hand has been shown in ' + message.channel.name)
  elif message.content.startswith(prefix + 'show-hand') and isinstance(message.channel, TextChannel):
    await message.channel.send(embed = get_hand_embed(message.author, get_user_hand(message.author)))

  if (message.content.startswith(prefix + 'shuffle') or message.content.startswith(prefix + 'reshuffle')) and isinstance(message.channel, TextChannel):
    if not check_dealer_role(message.author):
      await send_error_embed(message.channel, 'You are not the dealer')
      return
    deck = Deck()
    dealt_hands = {}
    await message.channel.send('Deck has been reshuffled. Number of cards in deck: ' + str(deck.number_of_cards_remaining()))

def store_channel(channel: TextChannel):
  db["channel"] = channel.id

def retrieve_channel():
  return client.get_channel(db["channel"])

async def send_error_embed(channel: TextChannel, errorMessage: str):
  embedDict = {
    "title": "Error!",
    "type": "rich",
    "description": errorMessage,
    "color": 16711680
  }
  await channel.send(embed = Embed.from_dict(embedDict))

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

keep_alive()
client.run(os.getenv('TOKEN'))
