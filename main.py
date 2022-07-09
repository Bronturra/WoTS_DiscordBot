import asyncio
import time
import discord
import requests
from discord.ext import commands
from requests.exceptions import HTTPError
from datetime import datetime, date

# Read DiscordToken from File when Script starts
with open("DiscordToken.txt") as f:
    discordToken = f.read().rstrip("\n")

# Read WoTAPIKey from File when Script starts
with open("WoTAPIKey.txt") as f:
    apiKey = f.read().rstrip("\n")

# Global variables
WoTAPIKey = apiKey
DiscordToken = discordToken
client = commands.Bot(command_prefix='!')
successfulCheckmark = 'https://emojipedia-us.s3.amazonaws.com/source/skype/289/check-mark_2714-fe0f.png'
unsuccessfulCheckmark = 'https://thumbs.dreamstime.com/b/check-marks-red-cross-icon-simple-vector-illustration-140098693.jpg'
infoCheckmark = 'https://previews.123rf.com/images/vanreeell/vanreeell2101/vanreeell210100291/162736118-.jpg'


# This function is executed after the program started to execute and is ready
@client.event
async def on_ready():
    print('[WoTS] Bot started:')
    print(f'[WoTS] UserName: {client.user.name}\n[WoTS] UserID: {client.user.id}\n------------------')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('!wots_help'))


# This command is executed after a user send the command "!info" in discord
@client.command()
async def wots_help(ctx):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !wots_help')
    embed = discord.Embed(
        title=f'@{ctx.author} - Here is a list of all Bot Commands:',
        description="The following Commands are accepted:",
        colour=discord.Colour.from_rgb(240, 204, 46)
    )
    embed.set_author(icon_url=infoCheckmark, name='List of Commands:')
    embed.add_field(name='!wots_help', value='Displays all available commands.', inline=False)
    embed.add_field(name='!info', value='Displays all the Player stats.\nSyntax: **!info** YourUserNameHere', inline=False)
    embed.set_footer(text=f'Information created on {date.today()} at {time.strftime("%H:%M:%S")}')
    await ctx.send(embed=embed)


# This command is executed after a user send the command "!info" in discord
@client.command()
async def info(ctx, userName):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !info {userName}')
    matchFound = False

    async with ctx.typing():
        await asyncio.sleep(0.125)

    try:
        # Fetch all informations
        url = f'https://api.worldoftanks.eu/wot/account/list/?application_id={WoTAPIKey}&search={userName}'
        response = requests.get(url).json()
        # Listings
        status = response['status']  # Returns 'ok' if successful
        meta = response['meta']['count']  # Returns count of possible findings
        # Process response body
        if status == 'ok' and meta == 0:  # Request unsuccessful - no player found
            embed = discord.Embed(
                title=f'Could not find an entry for User "{userName}".',
                colour=discord.Colour.red()
            )
            embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful')
            embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(embed=embed)
        elif status == 'ok' and meta == 1:  # Request successful and only one user found
            userName = response['data'][0]['nickname']  # Returns WOT-Username
            userID = response['data'][0]['account_id']  # Returns WOT-AccountID
            asyncio.create_task(get_user_data(str(userID), str(userName), ctx))  # Fetch all Account Informations
        elif status == 'ok' and meta > 1:  # Request successful and multiple user found
            for i in range(len(response['data'])):  # traverse to reponse body / data dictionary
                if response['data'][i]['nickname'] == userName:  # exact user found
                    matchFound = True
                    userName = response['data'][i]['nickname']  # Returns WOT-Username
                    userID = response['data'][i]['account_id']  # Returns WOT-UserID
                    asyncio.create_task(get_user_data(str(userID), str(userName), ctx))  # process further information
            if not matchFound:  # no user found, display possible users
                embed = discord.Embed(
                    title=f'Could not find an entry for User "{userName}".',
                    colour=discord.Colour.red()
                )
                embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful')
                for i in range(len(response['data'])):
                    userName = response['data'][i]['nickname']  # Returns WOT-Username
                    userID = response['data'][i]['account_id']  # Returns WOT-UserID
                    embed.add_field(name='Possible Finding:', value=f'User: {userName}, UserID: {userID}', inline=False)
                embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
                await ctx.send(embed=embed)
        else:  # Error occurred
            embed = discord.Embed(
                title='Try again.',
                colour=discord.Colour.red()
            )
            embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Error.')
            embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(embed=embed)
    except HTTPError as http_err: # HTTP Error occurred
        embed = discord.Embed(
            title='Request error.',
            description=f'{http_err}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='HTTP Error.')
        embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)
    except Exception as err:
        # Listings
        status = response['status']  # Returns 'ok' if successful
        error = response['error']['message']
        embed = discord.Embed(
            title='Request error.',
            description=f'Status: {status}, Error: {error}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='Error.')
        embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)


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
            #isInClan = False if clan_id=None else isInClan = True
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
                title=f'User: {nickname}\nID: {accountID}',
                description="The following information was found:",
                colour=discord.Colour.green()
            )
            embed.set_author(icon_url=successfulCheckmark, name='Request Successful')
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
            embed.set_footer(text=f'Information created on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(embed=embed)

        else:  # Error occurred
            embed = discord.Embed(
                title='Try again.',
                colour=discord.Colour.red()
            )
            embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Error.')
            embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(embed=embed)
    except HTTPError as http_err:
        embed = discord.Embed(
            title='Request error.',
            description=f'{http_err}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='HTTP Error.')
        embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)
    except Exception as err:
        # Listings
        status = response['status']  # Returns 'ok' if successful
        error = response['error']['message']
        embed = discord.Embed(
            title='Request error.',
            description=f'Status: {status}, Error: {error}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='Error.')
        embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)


# This command is executed after a user send the command "!info" in discord
@client.command()
async def tanks(ctx, userID):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !tanks {userID}')

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


client.run(DiscordToken)
# await ctx.send(f'Possible Finding: {userName} : {userID}')

