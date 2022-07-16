import locale
import discord
import asyncio
import time
import requests
from discord.ext import commands
from datetime import datetime, date
from data.tank_list import tanklist

# Variables
successfulCheckmark = 'https://emojipedia-us.s3.amazonaws.com/source/skype/289/check-mark_2714-fe0f.png'
unsuccessfulCheckmark = 'https://thumbs.dreamstime.com/b/check-marks-red-cross-icon-simple-vector-illustration-140098693.jpg'
language = 'en'
locale.setlocale(locale.LC_ALL, '')

# Read WoTAPIKey from File when Script starts
with open("Tokens/WoTAPIKey.txt") as f:
    # Read WoTAPIKey from File
    apiKey = f.read().rstrip("\n")
    f.close()


# This command is executed after a user send the command "!stats" in discord
@commands.command()
async def stats(ctx, userName):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !stats {userName}')
    # Variables
    region = 'eu'
    matchFound = False

    async with ctx.typing():
        await asyncio.sleep(0.125)

    try:
        # Fetch all informations
        urlList = f'https://api.worldoftanks.{region}/wot/account/list/?application_id={apiKey}&search={userName}'
        response = requests.get(urlList).json()
        # Listings
        status = response['status']  # Returns 'ok' if successful
        meta = response['meta']['count']  # Returns count of possible findings
        # Process response body
        if status == 'ok' and meta == 0:  # Request unsuccessful - no player found
            embed = discord.Embed(
                title=f'Could not find an entry for User "{userName}".',
                colour=discord.Colour.red()
            )
            embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful.')
            embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(embed=embed)
        elif status == 'ok' and meta == 1:  # Request successful and only one user found
            userName = response['data'][0]['nickname']  # Returns WOT-Username
            userID = response['data'][0]['account_id']  # Returns WOT-AccountID
            asyncio.create_task(get_user_data(str(userID), str(userName), ctx))  # Fetch all Account Informations
        elif status == 'ok' and meta > 1:  # Request successful and multiple users found
            for i in range(len(response['data'])):  # traverse to reponse body / data dictionary
                if response['data'][i]['nickname'] == userName:  # exact user found
                    matchFound = True
                    userName = response['data'][i]['nickname']  # Returns WOT-Username
                    userID = response['data'][i]['account_id']  # Returns WOT-UserID
                    asyncio.create_task(get_user_data(str(userID), str(userName), ctx))  # Process further information
            if not matchFound:  # no user found, display possible users
                embed = discord.Embed(
                    title=f'Could not find an entry for User "{userName}".',
                    colour=discord.Colour.red()
                )
                embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful.')
                for i in range(len(response['data'])):
                    userName = response['data'][i]['nickname']  # Returns WOT-Username
                    userID = response['data'][i]['account_id']  # Returns WOT-UserID
                    embed.add_field(name='Possible Finding:', value=f'```{userName} | {userID}```', inline=False)
                embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
                await ctx.send(embed=embed)
        else:  # Error occurred
            embed = discord.Embed(
                title='Please try again. If this error persists, please contact me via PN.',
                colour=discord.Colour.red()
            )
            embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Error.')
            embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(embed=embed)
    except Exception as err:
        status = response['status']  # Returns error-status
        error = response['error']['message']  # Returns error-message
        embed = discord.Embed(
            title='Request error.',
            description=f'Error: {err}\nStatus: {status}, Error: {error}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='Exception Error.')
        embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)


async def get_user_data(userID, userName, ctx):
    try:
        # Variables
        region = 'eu'
        keyfind = False
        # Fetch all informations
        urlInfo = f'https://api.worldoftanks.{region}/wot/account/info/?application_id={apiKey}&account_id={userID}'
        response = requests.get(urlInfo).json()
        # Listings
        status = response['status']
        meta = response['meta']['count']
        if status == 'ok' and meta == 1:  # Request successful and player found
            accountID = f'{userID}'
            globalRating = response['data'][accountID]['global_rating']
            lastBattle = datetime.fromtimestamp(response['data'][accountID]['last_battle_time'])
            shots = response['data'][accountID]['statistics']['all']['shots']
            battles = response['data'][accountID]['statistics']['all']['battles']
            wins = response['data'][accountID]['statistics']['all']['wins']
            losses = response['data'][accountID]['statistics']['all']['losses']
            draws = response['data'][accountID]['statistics']['all']['draws']
            frags = response['data'][accountID]['statistics']['all']['frags']
            spotted = response['data'][accountID]['statistics']['all']['spotted']
            hits = response['data'][accountID]['statistics']['all']['hits']
            maxXP = response['data'][accountID]['statistics']['all']['max_xp']
            maxDMG = response['data'][accountID]['statistics']['all']['max_damage']
            maxFrags = response['data'][accountID]['statistics']['all']['max_frags']
            maxFragsTankID = response['data'][accountID]['statistics']['all']['max_frags_tank_id']
            tankingFactor = response['data'][accountID]['statistics']['all']['tanking_factor']
            damage = response['data'][accountID]['statistics']['all']['damage_dealt']
            avg_xp = response['data'][accountID]['statistics']['all']['battle_avg_xp']
            lumberjack = response['data'][accountID]['statistics']['trees_cut']

            embed = discord.Embed(
                title=f'__User:__ {userName}  |  __ID:__ {accountID}  |  __Personal Rating:__ {globalRating}\n',
                colour=discord.Colour.green()
            )
            embed.set_author(icon_url=successfulCheckmark, name='Request Successful')
            embed.add_field(
                name=f'__OVERALL STATISTICS:__',
                value=f'Following Statistics were found for **{userName}**:\nhttps://worldoftanks.eu/{language}/community/accounts/{accountID}-{userName}/\n', inline=False,)

            embed.add_field(name='__Battles:__', value=f'```{locale.format_string("%d", battles)}```', inline=True)
            if battles == 0:
                embed.add_field(name='__Winrate:__', value=f'```{0}%```', inline=True)
            else:
                embed.add_field(name='__Winrate:__', value=f'```{(wins / battles)* 100:.02f}%```', inline=True)
            embed.add_field(name='__Last Battle:__', value=f'```{lastBattle.time()}  |  {lastBattle.date()}```', inline=True)

            embed.add_field(name='__Wins:__', value=f'```{locale.format_string("%d", wins)}```', inline=True)
            embed.add_field(name='__Losses:__', value=f'```{locale.format_string("%d", losses)}```', inline=True)
            embed.add_field(name='__Draws:__', value=f'```{locale.format_string("%d", draws)}```', inline=True)

            if shots == 0:
                embed.add_field(name='__Hits:__', value=f'```{0}%```', inline=True)
            else:
                embed.add_field(name='__Hits:__', value=f'```{(hits / shots)*100:.02f}%```', inline=True)
            embed.add_field(name='__Frags:__', value=f'```{locale.format_string("%d", frags)}```', inline=True)
            embed.add_field(name='__Spots:__', value=f'```{locale.format_string("%d", spotted)}```', inline=True)

            embed.add_field(name='__AVG Battle Experience:__', value=f'```{avg_xp}```', inline=True)
            if battles == 0:
                embed.add_field(name='__AVG Battle Damage:__', value=f'```{0}```', inline=True)
            else:
                embed.add_field(name='__AVG Battle Damage:__', value=f'```{(damage / battles):.00f}```', inline=True)
            if battles == 0:
                embed.add_field(name='__AVG Battle Frags:__', value=f'```{0}```', inline=True)
            else:
                embed.add_field(name='__AVG Battle Frags:__', value=f'```{(frags / battles):.02f}```', inline=True)

            embed.add_field(name='__MAX Battle Experience:__', value=f'```{maxXP}```', inline=True)
            embed.add_field(name='__MAX Battle Damage:__', value=f'```{maxDMG}```', inline=True)

            for key in tanklist:
                print(f'Key:{key} -> ID:{maxFragsTankID}, Identical: {key == maxFragsTankID}')
                if key == maxFragsTankID:
                    print('Identical!')
                    embed.add_field(name='__MAX Battle Frags:__', value=f'```{maxFrags} ({tanklist[maxFragsTankID]})```', inline=True)
                    keyfind = True
                    break
            print(keyfind)
            if keyfind == True:
                embed.add_field(name='__MAX Battle Frags:__', value=f'```{maxFrags} ({tanklist[maxFragsTankID]})```', inline=True)
            else:
                embed.add_field(name='__MAX Battle Frags:__', value=f'```{maxFrags} ({maxFragsTankID})```', inline=True)
            embed.add_field(name='__Tanking Factor:__', value=f'```{tankingFactor}```', inline=True)
            embed.add_field(name='__Lumberjack:__', value=f'```{lumberjack} Trees cut.```', inline=True)

            embed.set_footer(text=f'Information created on {date.today()} at {time.strftime("%H:%M:%S")}')
            #await ctx.send(f'{ctx.author.mention}', embed=embed)
            await ctx.reply(embed=embed)
        else:  # Error occurred
            embed = discord.Embed(
                title='Try again.',
                colour=discord.Colour.red()
            )
            embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Error.')
            embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
            await ctx.send(embed=embed)
    except Exception as err:
        status = response['status']  # Returns error-status
        error = response['error']['message']  # Returns error-message
        embed = discord.Embed(
            title='Request error.',
            description=f'Error: {err}\nStatus: {status}, Error: {error}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='Exception Error.')
        embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)


# Add Commands to the DiscordBot
def setup(bot):
    bot.add_command(stats)
