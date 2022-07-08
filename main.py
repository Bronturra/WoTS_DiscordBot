import asyncio
import discord
from discord.ext import commands
import requests
from requests.exceptions import HTTPError
from datetime import datetime

with open("DiscordToken.txt") as f:
    discordToken = f.read().rstrip("\n")

with open("WoTAPIKey.txt") as f:
    apiKey = f.read().rstrip("\n")

WoTAPIKey = apiKey
DiscordToken = discordToken


description = '''WoT-Statistic & more!'''
client = commands.Bot(command_prefix='!', description=description)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command()
async def info(ctx, userName):
    isEntryFoundinDB = False
    try:
        # Fetch all informations
        urlName = f'https://api.worldoftanks.eu/wot/account/list/?application_id={WoTAPIKey}&search={userName}'
        response = requests.get(urlName).json()
        # Listings
        status = response['status']  # Returns 'ok' if successful
        meta = response['meta']['count']  # Returns count of possible findings

        if status == 'ok' and meta == 0:  # Request successful but no player found
            await ctx.send('No Player available with this name.')
            pass
        elif status == 'ok' and meta == 1:  # Request successful and only one player found
            userName = response['data'][0]['nickname']  # Returns WOT-Username
            accountID = response['data'][0]['account_id']  # Returns WOT-AccountID
            asyncio.create_task(get_user_data(str(accountID), str(userName), ctx))  # Fetch all Account Informations
        elif status == 'ok' and meta > 1:
            for i in range(len(response['data'])):
                if response['data'][i]['nickname'] == userName:
                    isEntryFoundinDB = True
                    userName = response['data'][i]['nickname']  # Returns WOT-Username
                    accountID = response['data'][i]['account_id']  # Returns WOT-AccountID
                    asyncio.create_task(get_user_data(str(accountID), str(userName), ctx))
            if not isEntryFoundinDB:
                await ctx.send(f'No user with name "{userName}" found.')
        else:  # Error occurred
            await ctx.send('Request error.')
            pass
    except HTTPError as http_err:
        await ctx.send(f'HTTPError {http_err} occurred.')
    except Exception as err:
        await ctx.send(f'Error {err} occurred.')


async def get_user_data(accountID, accountName, ctx):
    try:
        # Fetch all informations
        urlAccount = f'https://api.worldoftanks.eu/wot/account/info/?application_id={WoTAPIKey}&account_id={accountID}'
        response = requests.get(urlAccount).json()
        # Listings
        status = response['status']
        meta = response['meta']['count']
        if status == 'ok' and meta == 1:  # Request successful and player found
            accountID = f'{accountID}'
            nickname = accountName  # response['data'][accountID]['nickname']  # Returns WOT-Username
            globalRating = response['data'][accountID]['global_rating']
            lastBattle = datetime.fromtimestamp(response['data'][accountID]['last_battle_time'])
            lastSeen = datetime.fromtimestamp(response['data'][accountID]['logout_at'])
            clan_id = response['data'][accountID]['clan_id']
            if clan_id is None:
                isInClan = False
            else:
                isInClan = True
            battles = response['data'][accountID]['statistics']['all']['battles']
            wins = response['data'][accountID]['statistics']['all']['wins']
            losses = response['data'][accountID]['statistics']['all']['losses']
            draws = response['data'][accountID]['statistics']['all']['draws']
            frags = response['data'][accountID]['statistics']['all']['frags']
            spotted = response['data'][accountID]['statistics']['all']['spotted']
            hits = response['data'][accountID]['statistics']['all']['hits']
            lifetimeXP = response['data'][accountID]['statistics']['all']['xp']
            maxXP = response['data'][accountID]['statistics']['all']['max_xp']
            maxDMG = response['data'][accountID]['statistics']['all']['max_damage']
            maxFrags = response['data'][accountID]['statistics']['all']['max_frags']
            tankingFactor = response['data'][accountID]['statistics']['all']['tanking_factor']

            embed = discord.Embed(
                title=f'Info for User {nickname} - ID {accountID}',
                #description="This is my description",
                colour=discord.Colour.purple()
            )
            embed.set_author(name='WoTS Bot')
            #embed.set_footer(text='this is my footer')

            embed.add_field(name='Global Rating', value=f'{globalRating}', inline=True)
            embed.add_field(name='Lifetime XP', value=f'{lifetimeXP}', inline=True)
            embed.add_field(name='Tanking Factor', value=f'{tankingFactor}', inline=True)
            embed.add_field(name='Battles', value=f'{battles}', inline=True)
            embed.add_field(name='Last Battle', value=f'{lastBattle}', inline=True)
            embed.add_field(name='Last Seen', value=f'{lastSeen}', inline=True)
            embed.add_field(name='Wins', value=f'{wins}', inline=True)
            embed.add_field(name='Losses', value=f'{losses}', inline=True)
            embed.add_field(name='Draws', value=f'{draws}', inline=True)
            embed.add_field(name='Hits', value=f'{hits}', inline=True)
            embed.add_field(name='Frags', value=f'{frags}', inline=True)
            embed.add_field(name='Spots', value=f'{spotted}', inline=True)
            embed.add_field(name='Maximum XP', value=f'{maxXP}', inline=True)
            embed.add_field(name='Maximum Frags', value=f'{maxFrags}', inline=True)
            embed.add_field(name='Maximum DMG', value=f'{maxDMG}', inline=True)

            await ctx.send(embed=embed)

        else:  # Error occurred
            await ctx.send('Request error.')
            pass
    except HTTPError as http_err:
        await ctx.send(f'HTTPError {http_err} occurred.')
    except Exception as err:
        await ctx.send(f'Error {err} occurred.')


def get_user_tanks(userAccountID):
    # urlAccountTanks = f''
    response = requests.get(
        'https://api.worldoftanks.eu/wot/account/tanks/?application_id=' + WoTAPIKey + '&account_id=' + userAccountID)
    user_json = response.json()
    print(user_json)


client.run(DiscordToken)
