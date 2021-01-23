import random
from discord import Client

client = Client()

cardSuits = ('Spades', 'Diamonds', 'Hearts', 'Clubs')
cardValues = ('Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King')

cardEmoji = {
  'Spades': {
    'Ace': '<:sa1:802645296651436033>',
    '2': '<:s2:802645296857350174>',
    '3': '<:s3:802645296780935218>',
    '4': '<:s4:802645296974397450>',
    '5': '<:s5:802645296801644595>',
    '6': '<:s6:802645296726671386>',
    '7': '<:s7:802645296797712404>',
    '8': '<:s8:802645296781721630>',
    '9': '<:s9:802645296777396264>',
    '10': '<:s10:802645297086988354>',
    'Jack': '<:sj:802645297149771795>',
    'Queen': '<:sq:802645296806625330>',
    'King': '<:sk:802645296639115305>'
  },
  'Diamonds': {
    'Ace': '<:da:802648589264355339>',
    '2': '<:d2:802648589096452147>',
    '3': '<:d3:802648589330808842>',
    '4': '<:d4:802648589229752362>',
    '5': '<:d5:802648589276676136>',
    '6': '<:d6:802648589151109121>',
    '7': '<:d7:802648589267894332>',
    '8': '<:d8:802648589347324014>',
    '9': '<:d9:802648589271957524>',
    '10': '<:d10:802648589037207564>',
    'Jack': '<:dj:802648589439336468>',
    'Queen': '<:dq:802648589260029962>',
    'King': '<:dk:802648589302104115>'
  },
  'Hearts': {
    'Ace': '<:ha:802648527879798855>',
    '2': '<:h2:802648527774679080>',
    '3': '<:h3:802648527381200937>',
    '4': '<:h4:802648527548317737>',
    '5': '<:h5:802648527766945832>',
    '6': '<:h6:802648527779790868>',
    '7': '<:h7:802648527401517059>',
    '8': '<:h8:802648527946776626>',
    '9': '<:h9:802648527456043019>',
    '10': '<:h10:802648527842967552>',
    'Jack': '<:hj:802648527884124170>',
    'Queen': '<:hq:802648527888842772>',
    'King': '<:hk:802648527460892682>'
  },
  'Clubs': {
    'Ace': '<:ca:802649255570964480>',
    '2': '<:c2:802649255238959151>',
    '3': '<:c3:802649255520501761>',
    '4': '<:c4:802649255314718755>',
    '5': '<:c5:802649255562838106>',
    '6': '<:c6:802649255553531985>',
    '7': '<:c7:802649255297941546>',
    '8': '<:c8:802660812678234122>',
    '9': '<:c9:802649255692337172>',
    '10': '<:c10:802660813105266768>',
    'Jack': '<:cj:802660812681379860>',
    'Queen': '<:cq:802660812736561172>',
    'King': '<:ck:802649255197278249>'
  }
}

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
    emoji = cardEmoji[self.suit][self.value]    
    return emoji

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

  def get_blank_card():
    return '<:blank:802649255524958281>'

  def get_cat_card():
    return '<:catcard:802649255549337610>'
