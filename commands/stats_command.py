import locale
import discord
import asyncio
import time
import requests
from discord.ext import commands
from requests.exceptions import HTTPError
from datetime import datetime, date

successfulCheckmark = 'https://emojipedia-us.s3.amazonaws.com/source/skype/289/check-mark_2714-fe0f.png'
unsuccessfulCheckmark = 'https://thumbs.dreamstime.com/b/check-marks-red-cross-icon-simple-vector-illustration-140098693.jpg'
infoCheckmark = 'https://previews.123rf.com/images/vanreeell/vanreeell2101/vanreeell210100291/162736118-.jpg'
language = 'en'
locale.setlocale(locale.LC_ALL, '')

# Read WoTAPIKey from File when Script starts
with open("Tokens/WoTAPIKey.txt") as f:
    apiKey = f.read().rstrip("\n")
    f.close()

# Global variables
WoTAPIKey = apiKey


# This command is executed after a user send the command "!stats" in discord
@commands.command()
async def stats(ctx, userName):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !stats {userName}')
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
            #hits = response['data'][accountID]['statistics']['all']['hits']
            shots = response['data'][accountID]['statistics']['all']['shots']
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
            maxFragsTankID = response['data'][accountID]['statistics']['all']['max_frags_tank_id']
            tankingFactor = response['data'][accountID]['statistics']['all']['tanking_factor']
            damage = response['data'][accountID]['statistics']['all']['damage_dealt']
            avg_xp = response['data'][accountID]['statistics']['all']['battle_avg_xp']
            lumberjack = response['data'][accountID]['statistics']['trees_cut']

            embed = discord.Embed(
                title=f'__User:__ {nickname}  |  __ID:__ {accountID}  |  __Personal Rating:__ {globalRating}\n',
                colour=discord.Colour.green()
            )
            embed.set_author(icon_url=successfulCheckmark, name='Request Successful')
            #embed.add_field(name=f'__OVERALL STATISTICS:__\nhttps://worldoftanks.eu/{language}/community/accounts/{accountID}-{nickname}\n', value=f'Following Statistics were found for **{nickname}**:', inline=False)
            embed.add_field(
                name=f'__OVERALL STATISTICS:__',
                value=f'Following Statistics were found for **{nickname}**:\nhttps://worldoftanks.eu/{language}/community/accounts/{accountID}-{nickname}\n', inline=False)

            embed.add_field(name='__Battles:__', value=f'```{locale.format_string("%d", battles, 1)}```', inline=True)
            embed.add_field(name='__Winrate:__', value=f'```{(wins/battles)*100:.02f}%```', inline=True)
            embed.add_field(name='__Last Battle:__', value=f'```{lastBattle.time()}  |  {lastBattle.date()}```', inline=True)

            embed.add_field(name='__Wins:__', value=f'```{locale.format_string("%d", wins, 1)}```', inline=True)
            embed.add_field(name='__Losses:__', value=f'```{locale.format_string("%d", losses, 1)}```', inline=True)
            embed.add_field(name='__Draws:__', value=f'```{locale.format_string("%d", draws, 1)}```', inline=True)

            embed.add_field(name='__Hits:__', value=f'```{(hits / shots)*100:.02f}%```', inline=True)
            embed.add_field(name='__Frags:__', value=f'```{locale.format_string("%d", frags, 1)}```', inline=True)
            embed.add_field(name='__Spots:__', value=f'```{locale.format_string("%d", spotted, 1)}```', inline=True)

            embed.add_field(name='__AVG Battle Experience:__', value=f'```{avg_xp}```', inline=True)
            embed.add_field(name='__AVG Battle Damage:__', value=f'```{(damage / battles):.00f}```', inline=True)
            embed.add_field(name='__AVG Battle Frags:__', value=f'```{(frags / battles):.02f}```', inline=True)

            embed.add_field(name='__MAX Battle Experience:__', value=f'```{maxXP}```', inline=True)
            embed.add_field(name='__MAX Battle Damage:__', value=f'```{maxDMG}```', inline=True)
            embed.add_field(name='__MAX Battle Frags:__', value=f'```{maxFrags} | {maxFragsTankID}```', inline=True)

            embed.add_field(name='__Tanking Factor:__', value=f'```{tankingFactor}```', inline=True)
            embed.add_field(name='__Lumberjack:__', value=f'```{lumberjack} Trees died.```', inline=True)
            #embed.add_field(name='Last Seen', value=f'{lastSeen}', inline=True)

            embed.set_footer(text=f'Information created on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(f'{ctx.author.mention}', embed=embed)

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
        await ctx.send(f'{ctx.author.mention}', embed=embed)


# Add Commands to the DiscordBot
def setup(bot):
    bot.add_command(stats)

