import random

cardSuits = ('Spades', 'Diamonds', 'Hearts', 'Clubs')
cardValues = ('Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King')

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
    return self.value + ' of ' + self.suit

class Deck:
  def __init__(self):
    self.cards = []
    for suit in cardSuits:
      for value in cardValues:
        self.cards.append(Card(suit, value))

  def number_of_cards_remaining(self):
    return len(self.cards)

  def take_random_card_from_deck(self):
    cardToPick = random.choice(self.cards)
    self.cards.remove(cardToPick)
    return cardToPick
