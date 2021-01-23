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
from cards import Card
from cards import Deck
from keep_alive import keep_alive
from helper import Helper

client = Client()
deck = Deck()
dealt_hands = {}
prefix = '$'

def play_card(user: User, index: int):
  userHand = get_user_hand(user)
  card = userHand.pop(index)
  return card

def get_card_embed(user: User, card: Card):
  cardDict = {
    "title": user.display_name + " plays the following card:",
    "type": "rich",
    "description": str(card),
    "color": 0x008000
  }
  return Embed.from_dict(cardDict)

def get_blank_card_embed(user: User):
  cardDict = {
    "title": user.display_name + " plays the following card:",
    "type": "rich",
    "description": Deck.get_blank_card(),
    "color": 0x008000
  }
  return Embed.from_dict(cardDict)

def get_cat_embed(user: User):
  cardDict = {
    "title": user.display_name + " plays the following card:",
    "type": "rich",
    "description": Deck.get_cat_card(),
    "color": 0x008000
  }
  return Embed.from_dict(cardDict)

def get_hand_embed(user: User, hand: []):
  handDict = {
    "title": user.display_name + "'s hand:",
    "type": "rich",
    "color": 0xFF0000 if hand is None or len(hand) == 0 else 0x008000
  }
  handDict['description'] = ''
  if hand is not None:
    for i in range(len(hand)):
      card = hand[i]
      handDict['description'] = handDict['description'] + str(card)
  return Embed.from_dict(handDict)

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
    for i in range(len(hand)):
      card = hand[i]
      handString = handString + str(i + 1) + str(card)
  return handString

async def send_hand_to_user(user: User):
  await user.send(embed = get_hand_embed(user, get_user_hand(user)))

def deal_hand(user: User, numberOfCards: int):
  hand = []
  for i in range(numberOfCards):
    card = deck.take_random_card_from_deck()
    hand.append(card)
  dealt_hands[user.id] = hand

def deal_cards(user: User, numberOfCards: int):
  for i in range(numberOfCards):
    card = deck.take_random_card_from_deck()
    if user.id not in dealt_hands or dealt_hands[user.id] is None:
      dealt_hands[user.id] = []
    dealt_hands[user.id].append(card)

def find_card_index(hand: [], suit: str, value: str):
  if hand is None or len(hand) == 0 or suit is None or suit == '' or value is None or value == '':
    return
  
  value = value.capitalize()
  suit = suit.capitalize()
  if suit[-1] != 's':
    suit = suit + 's'

  for i in range(len(hand)):
    card = hand[i]
    if card.suit == suit and card.value == value:
      return i

def get_dealer_role(guild: Guild):
  return guild.get_role(db['dealer_role'])

async def check_dealer_role(member: Member):
  dealerRole = get_dealer_role(member.guild)
  if dealerRole is None:
    await send_error_embed(retrieve_channel(), 'No dealer role set up, please use `$dealer-role [role]` to set one up')
    return False
  return dealerRole in member.roles

async def send_message(message: Message):
  global deck
  global dealt_hands
  global prefix
  if message.author == client.user:
    return

  ### Change prefix
  if message.content.startswith(prefix + 'prefix') and isinstance(message.channel, TextChannel) and message.author.guild_permissions.administrator :
    prefixText = re.search(rf'{re.escape(prefix)}prefix (\S+)', message.content)
    if prefixText is not None and prefixText.group(1) is not None:
      prefix = prefixText.group(1)
      await message.channel.send('Prefix has been changed to `' + prefix + '`')
    else:
      await message.channel.send('Prefix is `' + prefix + '`')
  elif message.content.startswith(prefix + 'prefix') and isinstance(message.channel, TextChannel) and not message.author.guild_permissions.administrator:
    await send_error_embed(message.channel, 'Administrator privledges required to change prefix')
  elif message.content.startswith(prefix + 'prefix') and not isinstance(message.channel, TextChannel):
    await send_error_embed(message.channel, 'Cannot change prefix from DMs')

  ### Show/Change dealer role
  if message.content.startswith(prefix + 'dealer-role') and isinstance(message.channel, TextChannel):
    if message.role_mentions is not None and len(message.role_mentions) > 0:
      if message.author.guild_permissions.administrator:
        db['dealer_role'] = message.role_mentions[0].id
      else:
        await message.channel.send('Administrator privledges required to change dealer role')
    await message.channel.send('**' + str(get_dealer_role(message.guild)) + '** role is the dealer role')

  ### Deal a hand to yourself/others
  if (message.content.startswith(prefix + 'deal-hand') or message.content.startswith(prefix + 'deal-card')) and isinstance(message.channel, TextChannel): 
    if not await check_dealer_role(message.author):
      await send_error_embed(message.channel, 'You are not the dealer')
      return

    mentionsPresent = message.mentions is not None and len(message.mentions) > 0
    store_channel(message.channel) # Store the channel the messgage was sent from for later

    handRegex = rf'{re.escape(prefix)}deal-hands?'
    cardRegex = rf'{re.escape(prefix)}deal-cards?'

    numberText = re.search(rf'{re.escape(prefix)}deal(?:-hand|-cards?)? (\d+)', message.content)
    number = 1 if re.match(cardRegex, message.content) else 2 # default number of cards to deal
    if numberText is not None and numberText.group(1) is not None:
      number = int(numberText.group(1))
    if (not mentionsPresent and number > deck.number_of_cards_remaining()) or (mentionsPresent and number * len(message.mentions) > deck.number_of_cards_remaining()):
      await send_error_embed(message.channel, 'Not enough cards left in deck to deal hand')
      return

    if re.match(cardRegex, message.content): # Deal card(s) to existing hand
      if mentionsPresent:
        for person in message.mentions:
          deal_cards(person, number)
          await send_hand_to_user(person)
        await message.channel.send('Dealt everyone a card in their DMs. Number of cards remaining in deck: ' + str(deck.number_of_cards_remaining()))
      else:
        deal_cards(message.author, number)
        await send_hand_to_user(message.author)
        await message.channel.send('Dealt you a card. Check your DMs. Number of cards remaining in deck: ' + str(deck.number_of_cards_remaining()))

    elif re.match(handRegex, message.content): # Deal an entire new hand
      if mentionsPresent:
        for person in message.mentions:
          deal_hand(person, number)
          await send_hand_to_user(person)
        await message.channel.send('Dealt everyone a hand in their DMs. Number of cards remaining in deck: ' + str(deck.number_of_cards_remaining()))
      else:
        deal_hand(message.author, number)
        await send_hand_to_user(message.author)
        await message.channel.send('Dealt you a hand. Check your DMs. Number of cards remaining in deck: ' + str(deck.number_of_cards_remaining()))

  elif message.content.startswith(prefix + 'deal') and not isinstance(message.channel, TextChannel):
    await message.channel.send('Cannot deal hand from DMs.')

  ### Add another deck of cards
  if message.content.startswith(prefix + 'add-deck') and isinstance(message.channel, TextChannel):
    if not await check_dealer_role(message.author):
      await send_error_embed(message.channel, 'You are not the dealer')
      return
    deck.add_deck()
    await message.channel.send('Deck added. Number of cards in deck: ' + str(deck.number_of_cards_remaining()))

  ### Show your hand to the table
  if message.content.startswith(prefix + 'show-hand') and isinstance(message.channel, DMChannel):
    returnChannel = retrieve_channel()
    await returnChannel.send(embed = get_hand_embed(message.author, get_user_hand(message.author)))
    await message.channel.send(f'Your hand has been shown in #{returnChannel} on `{returnChannel.guild}`')
  elif message.content.startswith(prefix + 'show-hand') and isinstance(message.channel, TextChannel):
    await message.channel.send(embed = get_hand_embed(message.author, get_user_hand(message.author)))

  ### Peek at your hand
  if message.content.startswith(prefix + 'peek') and isinstance(message.channel, DMChannel):
    await message.channel.send('Your hand:', embed = get_hand_embed(message.author, get_user_hand(message.author)))
  
  ### Play card
  if message.content.startswith(prefix + 'play') and isinstance(message.channel, DMChannel):
    returnChannel = retrieve_channel()
    member = await returnChannel.guild.fetch_member(message.author.id)
    
    userHand = get_user_hand(member)
    if userHand is None: # User has no hand
      await send_error_embed(message.channel, 'You have no hand, ask someone to deal you one')
      return

    cardRegexSearch = re.search(rf'{re.escape(prefix)}play(?:-card)? (\w+) (\w+)', message.content)
    numberText = re.search(rf'{re.escape(prefix)}play(?:-card)? (\d+)', message.content)
    number: int

    if cardRegexSearch is not None:
      number = find_card_index(userHand, cardRegexSearch.group(1), cardRegexSearch.group(2))
      if number is None:
        await send_error_embed(message.channel, 'Requested card not found in your hand')
        return
    elif numberText is not None and numberText.group(1) is not None:
      number = int(numberText.group(1))
      number = number - 1
      if number < 0 or number > len(userHand) - 1: # User picks an invalid number
        await send_error_embed(message.channel, 'Not a valid number for the amount of cards your hand has')
        return
    else: # No number is given
      await send_error_embed(message.channel, 'Please provide the number of the card you wish to play')
      return
    
    card = play_card(member, number) # Removes card from player hand
    cardEmbed = get_card_embed(member, card)
    await returnChannel.send(embed = cardEmbed)
    await message.channel.send(f'You\'ve played the following card in #{returnChannel} on {returnChannel.guild}', embed = cardEmbed)

  ### Take back all cards and shuffle the deck
  if (message.content.startswith(prefix + 'shuffle') or message.content.startswith(prefix + 'reshuffle')) and isinstance(message.channel, TextChannel):
    if not await check_dealer_role(message.author):
      await send_error_embed(message.channel, 'You are not the dealer')
      return
    deck = Deck()
    dealt_hands = {}
    await message.channel.send('Deck has been reshuffled. Number of cards in deck: ' + str(deck.number_of_cards_remaining()))

  if message.content.startswith(prefix + 'blank'):
    await message.channel.send(embed = get_blank_card_embed(message.author))

  if message.content.startswith(prefix + 'cat'):
    await message.channel.send(embed = get_cat_embed(message.author))
  
  if message.content.startswith(prefix + 'help'):
    await message.channel.send(embed = Helper.get_help_embed())

def store_channel(channel: TextChannel):
  db["channel"] = channel.id

def retrieve_channel():
  return client.get_channel(db["channel"])

async def send_error_embed(channel: TextChannel, errorMessage: str):
  embedDict = {
    "title": "Error!",
    "type": "rich",
    "description": errorMessage,
    "color": 0xFF0000
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
