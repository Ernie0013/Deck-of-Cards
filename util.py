from replit import db
from discord import Client
from discord import Embed
from discord import TextChannel
from discord.abc import Messageable

class Util:
  def store_channel(channel: TextChannel):
    db["channel"] = channel.id

  def retrieve_channel(client: Client):
    return client.get_channel(db["channel"])

  async def send_error_embed(channel: Messageable, errorMessage: str):
    embedDict = {
      "title": "Error!",
      "type": "rich",
      "description": errorMessage,
      "color": 0xFF0000
    }
    await channel.send(embed = Embed.from_dict(embedDict))

  def get_help_embed():
    helpdDict = {
      "title": "Deck of Cards Help",
      "type": "rich",
      "description": "Below are the commands this bot can perform\n<> = required arguments\n[] = optional arguments",
      "color": 0xbdbdbd,
      "footer": {
        "text": "Created by Ernie Collins © 2021"
      },
      "fields": [
        {
          "name": "$prefix <prefix>",
          "value": "Changes the prefix which is used to call the commands. Only available to server administrators."
        },
        {
          "name": "$dealer-role <@Role>",
          "value": "Changes the role which is deemed to be the dealer. Only available to server administrators."
        },
        {
          "name": "$deal-hand [number of cards] [@User] [@Role]",
          "value": "Deals a hand to user's DMs. Default is 2 cards to the user using this command. Can be used to mention multiple users/roles at once. Only available to dealers."
        },
        {
          "name": "$deal-cards [number of cards] [@User] [@Role]",
          "value": "Adds a number of cards to the user's existing hand. Default is 1 card to the user using this command. Can be used to mention multiple users/roles at once. Only available to dealers."
        },
        {
          "name": "$show-hand",
          "value": "Show your hand in the channel the game is being played in. Can be used from DMs or directly in channel."
        },
        {
          "name": "$add-deck [number]",
          "value": "Adds one or more decks of cards to the current deck. Only available to dealers."
        },
        {
          "name": "$remove-deck [number]",
          "value": "Removes one or more decks of cards from the current deck. At least one deck will always remain. Only available to dealers."
        },
        {
          "name": "$reset-deck [number]",
          "value": "Works similarly to `$shuffle` but will change the number of decks to either the default of 1 or the number of decks given. Only available to dealers."
        },
        {
          "name": "$shuffle",
          "value": "Returns all cards to the deck and shuffles the deck. Only available to dealers."
        },
        {
          "name": "$peek",
          "value": "Show the current hand the player has. Only available in DMs. "
        },
        {
          "name": "$play-card <number>",
          "value": "Plays the specified card."
        },
        {
          "name": "$play-card <card suit> <card value>",
          "value": "Plays the specified card."
        },
        {
          "name": "$deck",
          "value": "Check the status of the current deck."
        },
        {
          "name": "$blank",
          "value": "Play a blank card."
        },
        {
          "name": "$help",
          "value": "This text you're reading right now."
        },
      ]
    }

    return Embed.from_dict(helpdDict)