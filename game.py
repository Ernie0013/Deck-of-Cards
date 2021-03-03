import re
from discord import Client
from discord import Message
from discord import DMChannel
from discord import Guild
from discord import Member
from discord import TextChannel
from discord import User
from replit import db
from cards import Card
from cards import Deck
from cards import Hand
from util import Util

class Game:
  def __init__(self, client:Client, channel):
    self.client = client
    self.channel = channel
    self.deck = Deck()
    self.dealt_hands = {}
    self.prefix = '$'
    self.hand_limit = 52
    self.number_of_decks = 1
    self.played_cards = {}

  def get_user_hand(self, member: Member):
    if member.id in self.dealt_hands:
      return self.dealt_hands[member.id]
    else:
      self.dealt_hands[member.id] = Hand(member, [])
      return self.dealt_hands[member.id]

  def get_user_hand_size(self, member: Member):
    hand = self.get_user_hand(member)
    if hand is None:
      return 0
    else:
      return len(hand)

  async def send_hand_to_user(self, member: Member):
    await member.send(f'You\'ve been sent a hand from {self.get_channel_name_and_guild()}', embed = self.get_user_hand(member).get_embed(self.channel))

  def deal_hand(self, user: User, number_of_cards: int):
    hand = self.deck.deal_hand(user, number_of_cards)
    self.dealt_hands[user.id] = hand

  def deal_cards(self, user: User, number_of_cards: int):
    self.deck.deal_cards(self.get_user_hand(user), number_of_cards)

  def get_dealer_role(self, guild: Guild):
    if guild.id in db:
      dealer_role_obj = db[guild.id]
      return guild.get_role(dealer_role_obj['dealer_role'])

  async def check_dealer_role(self, member: Member):
    dealerRole = self.get_dealer_role(member.guild)
    if dealerRole is None:
      await Util.send_error_embed(self.channel, 'No dealer role set up, please use `$dealer-role [role]` to set one up')
      return False
    return dealerRole in member.roles

  def get_channel_name_and_guild(self):
    return f'#{self.channel.mention} on `{self.channel.guild}`'

  def get_deck_status(self):
    return f'\nNumber of total decks in use: {self.deck.decks_in_use}\nNumber of cards remaining in deck: {self.deck.number_of_cards_remaining()}\nHands dealt: {len(self.dealt_hands)}'

  async def send_message(self, message: Message):
    if message.author == self.client.user: # Bot is not allowed to react to itself or it will get stuck in a loop
      return

    mentionsPresent = message.mentions is not None and len(message.mentions) > 0

    ### Change prefix
    if message.content.startswith(self.prefix + 'prefix') and isinstance(message.channel, TextChannel) and message.author.guild_permissions.administrator :
      prefixText = re.search(rf'{re.escape(self.prefix)}prefix (\S+)', message.content)
      if prefixText is not None and prefixText.group(1) is not None:
        prefix = prefixText.group(1)
        await message.channel.send('Prefix has been changed to `' + prefix + '`')
      else:
        await message.channel.send('Prefix is `' + prefix + '`')
    elif message.content.startswith(self.prefix + 'prefix') and isinstance(message.channel, TextChannel) and not message.author.guild_permissions.administrator:
      await Util.send_error_embed(message.channel, 'Administrator privledges required to change prefix')
    elif message.content.startswith(self.prefix + 'prefix') and not isinstance(message.channel, TextChannel):
      await Util.send_error_embed(message.channel, 'Cannot change prefix from DMs')

    ### Show/Change dealer role
    if message.content.startswith(self.prefix + 'dealer-role') and isinstance(message.channel, TextChannel):
      if message.role_mentions is not None and len(message.role_mentions) > 0:
        if message.author.guild_permissions.administrator:
          db[message.guild.id] = {'dealer_role': message.role_mentions[0].id}
        else:
          await Util.send_error_embed(message.channel, 'Administrator privledges required to change dealer role')
          return
      await message.channel.send('**' + str(self.get_dealer_role(message.guild)) + '** role is the dealer role')

    ### Deal a hand to yourself/others
    if (message.content.startswith(self.prefix + 'deal-hand') or message.content.startswith(self.prefix + 'deal-card')) and isinstance(message.channel, TextChannel): 
      if not await self.check_dealer_role(message.author):
        await Util.send_error_embed(message.channel, 'You are not the dealer')
        return

      Util.store_channel(message.channel) # Store the channel the messgage was sent from for later

      handRegex = rf'{re.escape(self.prefix)}deal-hands?'
      cardRegex = rf'{re.escape(self.prefix)}deal-cards?'

      numberText = re.search(rf'{re.escape(self.prefix)}deal(?:-hand|-cards?)? (\d+)', message.content)
      number = 1 if re.match(cardRegex, message.content) else 2 # default number of cards to deal
      if numberText is not None and numberText.group(1) is not None:
        number = int(numberText.group(1))
      if (not mentionsPresent and number > self.deck.number_of_cards_remaining()) or (mentionsPresent and number * len(message.mentions) > self.deck.number_of_cards_remaining()):
        await Util.send_error_embed(message.channel, 'Not enough cards left in deck to deal hand')
        return
      
      if not mentionsPresent and self.get_user_hand_size(message.author) + number > self.hand_limit:
        await Util.send_error_embed(message.channel, f'Cannot add {number} card(s). Limit for cards in a single hand is {self.hand_limit}.')
        return
      elif mentionsPresent:
        for person in message.mentions:
          if self.get_user_hand_size(person) + number > self.hand_limit:
            await Util.send_error_embed(message.channel, f'Could not deal cards. Adding {number} card(s) to {person.display_name}\'s hand would push their hand over the limit of {self.hand_limit} cards.')
            return

      if re.match(cardRegex, message.content): # Deal card(s) to existing hand
        if mentionsPresent:
          for person in message.mentions:
            self.deal_cards(person, number)
            await self.send_hand_to_user(person)
          await message.channel.send(f'Dealt everyone a card in their DMs.\n{self.get_deck_status()}')
        else:
          self.deal_cards(message.author, number)
          await self.send_hand_to_user(message.author)
          await message.channel.send(f'Dealt you a card. Check your DMs.\n{self.get_deck_status()}')

      elif re.match(handRegex, message.content): # Deal an entire new hand
        if mentionsPresent:
          for person in message.mentions:
            self.deal_hand(person, number)
            await self.send_hand_to_user(person)
          await message.channel.send(f'Dealt everyone a hand in their DMs.\n{self.get_deck_status()}')
        else:
          self.deal_hand(message.author, number)
          await self.send_hand_to_user(message.author)
          await message.channel.send(f'Dealt you a hand. Check your DMs.\n{self.get_deck_status()}')

    elif message.content.startswith(self.prefix + 'deal') and not isinstance(message.channel, TextChannel):
      await message.channel.send('Cannot deal hand from DMs.')

    ### Add another deck of cards
    if (message.content.startswith(self.prefix + 'add-deck') or message.content.startswith(self.prefix + 'remove-deck')) and isinstance(message.channel, TextChannel):
      if not await self.check_dealer_role(message.author):
        await Util.send_error_embed(message.channel, 'You are not the dealer')
        return
      number = 1
      numberText = re.search(rf'{re.escape(self.prefix)}(?:add|remove)-decks? (\d+)', message.content)
      if numberText is not None and numberText.group(1) is not None:
        number = int(numberText.group(1))

      if (message.content.startswith(self.prefix + 'remove')):
        if self.deck.decks_in_use == 1:
          await Util.send_error_embed(message.channel, 'Need to have at least one deck')
          return
        self.deck.remove_deck(number)
        await message.channel.send(f'Deck(s) removed.\n{self.get_deck_status()}')
      else:
        self.deck.add_deck(number)
        await message.channel.send(f'Deck(s) added.\n{self.get_deck_status()}')

    ### Show your hand to the table
    if message.content.startswith(self.prefix + 'show-hand') and isinstance(message.channel, DMChannel):
      await self.channel.send(embed = self.get_user_hand(message.author).get_embed(None))
      await message.channel.send(f'Your hand has been shown in {self.get_channel_name_and_guild()}')
    elif message.content.startswith(self.prefix + 'show-hand') and isinstance(message.channel, TextChannel):
      if mentionsPresent and not await self.check_dealer_role(message.author):
        await Util.send_error_embed(message.channel, 'Only the dealer can show other peoples\' hands')
      elif mentionsPresent:
        for person in message.mentions:
          await message.channel.send(embed = self.get_user_hand(person).get_embed(None))
      elif not mentionsPresent:
        await message.channel.send(embed = self.get_user_hand(message.author).get_embed(None))

    ### Peek at your hand
    if message.content.startswith(self.prefix + 'peek') and isinstance(message.channel, DMChannel):
      await message.channel.send('Your hand:', embed = self.get_user_hand(message.author).get_embed(self.channel))
    
    ### Play card
    if message.content.startswith(self.prefix + 'play'):
      member = await self.channel.guild.fetch_member(message.author.id)
      
      userHand = self.get_user_hand(member)
      if userHand is None: # User has no hand
        await Util.send_error_embed(message.channel, 'You have no hand, ask someone to deal you one')
        return

      cardRegexSearch = re.search(rf'{re.escape(self.prefix)}play(?:-card)? (\w+) (of)? ?((?!facedown)\w+) ?(facedown)?', message.content)
      numberText = re.search(rf'{re.escape(self.prefix)}play(?:-card)? (\d+) ?(facedown)?', message.content)
      
      if cardRegexSearch is not None:
        card = userHand.play_card(cardRegexSearch.group(1), cardRegexSearch.group(3), cardRegexSearch.group(4) is not None) if cardRegexSearch.group(2) is None else userHand.play_card(cardRegexSearch.group(3), cardRegexSearch.group(1), cardRegexSearch.group(4) is not None)
        if card is None:
          await Util.send_error_embed(message.channel, 'Requested card not found in your hand')
          return
      elif numberText is not None and numberText.group(1) is not None:
        number = int(numberText.group(1))
        number = number - 1
        if number < 0 or number > len(userHand) - 1: # User picks an invalid number
          await Util.send_error_embed(message.channel, 'Not a valid number for the amount of cards your hand has')
          return
        else:
          card = userHand.play_card_number(number, numberText.group(2) is not None)
      else: # No number or card description given
        await Util.send_error_embed(message.channel, 'Please provide the number of the card you wish to play')
        return
      
      cardEmbed = card.get_embed(member, None)
      sentMessage = await self.channel.send(embed = cardEmbed)
      self.played_cards[sentMessage.id] = card
      if self.channel != message.channel:
        await message.channel.send(f'You\'ve played the following card in {self.get_channel_name_and_guild()}', embed = cardEmbed)

    ### Turn up facedown card
    if message.content.startswith(self.prefix + 'turn-up') and isinstance(message.channel, TextChannel):
      if not await self.check_dealer_role(message.author):
        await Util.send_error_embed(message.channel, 'You are not the dealer')
        return
      if message.reference is None:
        await Util.send_error_embed(message.channel, 'Please reply to the message containing the card to turn up')
        return
      if message.reference.message_id not in self.played_cards:
        await Util.send_error_embed(message.channel, 'Message could not be found, make sure you\'re replying to a message containing a playing card')
        return
      
      member = await self.channel.guild.fetch_member(message.author.id)
      self.played_cards[message.reference.message_id].reveal()
      await self.channel.send(embed = self.played_cards[message.reference.message_id].get_embed(member, None))

    ### Take back all cards and shuffle the deck
    if (message.content.startswith(self.prefix + 'shuffle') or message.content.startswith(self.prefix + 'reshuffle') or message.content.startswith(self.prefix + 'reset-deck')) and isinstance(message.channel, TextChannel):
      if not await self.check_dealer_role(message.author):
        await Util.send_error_embed(message.channel, 'You are not the dealer')
        return

      numberText = re.search(rf'{re.escape(self.prefix)}reset-decks? (\d+)', message.content)
      if numberText is not None and numberText.group(1) is not None:
        self.deck.reset(int(numberText.group(1)))
      else:
        self.deck.reset()

      self.dealt_hands.clear()
      await message.channel.send(f'Deck has been reshuffled.\n{self.get_deck_status()}')

    ### Check deck status
    if message.content.startswith(self.prefix + 'deck'):
      await message.channel.send(f'Current deck.\n{self.get_deck_status()}')

    ### Show a blank card
    if message.content.startswith(self.prefix + 'blank'):
      await message.channel.send(embed = Card.get_blank_card_embed(message.author, message.channel))

    ### OWO
    if message.content.startswith(self.prefix + 'cat'):
      await message.channel.send(embed = Card.get_cat_embed(message.author, message.channel))
    
    ### Show the help information
    if message.content.startswith(self.prefix + 'help'):
      await message.author.send(embed = Util.get_help_embed())
      if not isinstance(message.channel, DMChannel):
        await message.channel.send('Help information sent. Check your DMs.')