from discord import Embed

class Helper:
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
          "name": "$deal-hand [number of cards] [@User]",
          "value": "Deals a hand to user's DMs. Default is 2 cards to the user using this command. Can be used to mention multiple users at once. Only available to dealers."
        },
        {
          "name": "$deal-cards [number of cards] [@User]",
          "value": "Adds a number of cards to the user's existing hand. Default is 1 card to the user using this command. Can be used to mention multiple users at once. Only available to dealers."
        },
        {
          "name": "$add-deck",
          "value": "Adds another deck of cards to the current deck. Only available to dealers."
        },
        {
          "name": "$peek",
          "value": "Show the current hand the player has. Only available in DMs. "
        },
        {
          "name": "$play-card <number>",
          "value": "Plays the specified card. Only available in DMs. "
        },
        {
          "name": "$play-card <card suit> <card value>",
          "value": "Plays the specified card. Only available in DMs. "
        },
        {
          "name": "$shuffle",
          "value": "Returns all cards to the deck and shuffles the deck. Only available to dealers."
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