import asyncio
import time
import requests
from discord.ext import commands
from datetime import datetime, date

# Read WoTAPIKey from File when Script starts
with open("Tokens/WoTAPIKey.txt") as f:
    apiKey = f.read().rstrip("\n")
    f.close()

# Global variables
WoTAPIKey = apiKey


# This command is executed after a user send the command "!tanks" in discord
@commands.command()
async def tank(ctx, userID):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !tank {userID}')

    async with ctx.typing():
        await asyncio.sleep(0.125)

    try:
        # Fetch all informations
        urlAccount = f'https://api.worldoftanks.eu/wot/account/tanks/?application_id={WoTAPIKey}&account_id={userID}'
        response = requests.get(urlAccount).json()
        # Listings
        status = response['status']
        meta = response['meta']['count']
        tanks = len(response['data'][f'{userID}'])

        if status == 'ok' and meta == 1:  # Request successful and player found
            await ctx.send(f'Tanks: {tanks}')

    except Exception as err:
        print(err)


# Add Commands to the DiscordBot
def setup(bot):
    bot.add_command(tank)
