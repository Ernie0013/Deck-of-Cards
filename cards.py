import random
from discord import Client

client = Client()

cardSuits = ('Spades', 'Diamonds', 'Hearts', 'Clubs')
cardValues = ('Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King')

suitEmojis = ('<:bspades:802184587395465237>', '<:rdiamonds:802184587521556521>','<:rhearts:802184587514085397>', '<:bclubs:802184587702042656>')
valueEmojisRed = ('<:ra:802184587757223966>', '<:r2:802184587660886093>', '<:r3:802184587979391006>', '<:r4:802184587974410260>', '<:r5:802184587715018782>', '<:r6:802184587672813619>', '<:r7:802184587718688818>', '<:r8:802184587798511677>', '<:r9:802184587710562305>', '<:r10:802184587845304340>', '<:rj:802184587760369684>', '<:rq:802184587971133531>', '<:rk:802184587647385681>')
valueEmojisBlack = ('<:ba:802184587563499531>', '<:b2:802184587530862604>', '<:b3:802184587182080031>', '<:b4:802184587316035595>', '<:b5:802184587605180456>', '<:b6:802184587593777162>', '<:b7:802184587589320715>', '<:b8:802184587572019250>', '<:b9:802184587593252886>', '<:b10:802184587186536499>', '<:bj:802184587680809000>', '<:bq:802184587668357170>', '<:bk:802184587663900702>')

class Card:
  def __init__(self, suit: cardSuits, value: cardValues):
    self.suit = suit
    self.value = value

  def __hash__(self):
    return self.suit.__hash__ + self.value.__hash__

  def __eq__(self, eq):
    if not isinstance(eq, Card):
      return False 
    return self.suit == eq.suit and self.value == eq.value

  def __str__(self):
    suitIndex = cardSuits.index(self.suit)
    valueIndex = cardValues.index(self.value)

    suitEmoji = suitEmojis[suitIndex]
    valueEmoji = valueEmojisBlack[valueIndex] if suitIndex == 0 or suitIndex == 3 else valueEmojisRed[valueIndex]

    return self.value + '\tof\t' + self.suit + '\n' + valueEmoji + '\n' + suitEmoji

class Deck:
  def __init__(self):
    self.cards = []
    self.add_deck()

  def add_deck(self):
    for suit in cardSuits:
      for value in cardValues:
        self.cards.append(Card(suit, value))

  def number_of_cards_remaining(self):
    return len(self.cards)

  def take_random_card_from_deck(self):
    cardToPick = random.choice(self.cards)
    self.cards.remove(cardToPick)
    return cardToPick
