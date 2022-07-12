import locale
import discord
import asyncio
import time
import requests
from discord.ext import commands
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
async def compare(ctx, firstUserName, secondUserName):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !compare {firstUserName} {secondUserName}')
    # Variables
    region = 'eu'
    matchFound = False

    async with ctx.typing():
        await asyncio.sleep(0.125)

    try:
        # Fetch all informations
        urlListFirstUser = f'https://api.worldoftanks.{region}/wot/account/list/?application_id={WoTAPIKey}&search={firstUserName}'
        urlListSecondUser = f'https://api.worldoftanks.{region}/wot/account/list/?application_id={WoTAPIKey}&search={secondUserName}'
        responseFirstUser = requests.get(urlListFirstUser).json()
        responseSecondUser = requests.get(urlListSecondUser).json()
        # Listings
        statusFirstUser = responseFirstUser['status']  # Returns 'ok' if successful
        statusSecondUser = responseSecondUser['status']  # Returns 'ok' if successful
        metaFirstUser = responseFirstUser['meta']['count']  # Returns count of possible findings
        metaSecondUser = responseSecondUser['meta']['count']  # Returns count of possible findings
        # Process response body
        if statusFirstUser == 'ok' and statusSecondUser == 'ok':  # Request unsuccessful - no player found
            if metaFirstUser == 0 and metaSecondUser == 0:
                embed = discord.Embed(
                    title=f'Could not find an entry for User "{firstUserName}" and "{secondUserName}".',
                    colour=discord.Colour.red()
                )
                embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful.')
                embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
                await ctx.send(embed=embed)
                return
            elif metaFirstUser == 0 and metaSecondUser == 1:
                embed = discord.Embed(
                    title=f'Could not find an entry for User "{firstUserName}".',
                    colour=discord.Colour.red()
                )
                embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful.')
                embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
                await ctx.send(embed=embed)
                return
            elif metaFirstUser == 1 and metaSecondUser == 0:
                embed = discord.Embed(
                    title=f'Could not find an entry for User "{secondUserName}".',
                    colour=discord.Colour.red()
                )
                embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful.')
                embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
                await ctx.send(embed=embed)
                return
        if statusFirstUser == 'ok' and statusSecondUser == 'ok':
            if metaFirstUser == 1 and metaSecondUser == 1:  # Request successful and only one user found
                firstUser = responseFirstUser['data'][0]['nickname']  # Returns WOT-Username
                firstUserID = responseFirstUser['data'][0]['account_id']  # Returns WOT-AccountID
                secondUser = responseSecondUser['data'][0]['nickname']  # Returns WOT-Username
                secondUserID = responseSecondUser['data'][0]['account_id']  # Returns WOT-AccountID
                asyncio.create_task(get_user_data(str(firstUserID), str(firstUser), str(secondUserID), str(secondUser), ctx))  # Fetch all Account Informations
            elif metaFirstUser > 1 and metaSecondUser == 1:  # Request successful and multiple users found
                for i in range(len(responseFirstUser['data'])):  # traverse to reponse body / data dictionary
                    if responseFirstUser['data'][i]['nickname'] == firstUserName:  # exact user found
                        matchFound = True
                        firstUser = responseFirstUser['data'][0]['nickname']  # Returns WOT-Username
                        firstUserID = responseFirstUser['data'][0]['account_id']  # Returns WOT-AccountID
                        secondUser = responseSecondUser['data'][0]['nickname']  # Returns WOT-Username
                        secondUserID = responseSecondUser['data'][0]['account_id']  # Returns WOT-AccountID
                        asyncio.create_task(get_user_data(str(firstUserID), str(firstUser), str(secondUserID), str(secondUser), ctx))  # Process further information
                if not matchFound:  # no user found, display possible users
                    embed = discord.Embed(
                        title=f'Could not find an entry for User "{firstUserName}".',
                        colour=discord.Colour.red()
                    )
                    embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Unsuccessful.')
                    for i in range(len(responseFirstUser['data'])):
                        userName = responseFirstUser['data'][i]['nickname']  # Returns WOT-Username
                        userID = responseFirstUser['data'][i]['account_id']  # Returns WOT-UserID
                        embed.add_field(name='Possible Finding:', value=f'```{userName} | {userID}```', inline=False)
                    embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
                    await ctx.send(embed=embed)
            elif metaFirstUser == 1 and metaSecondUser > 1:
                print('do something')
            else:  # Error occurred
                print(f'{statusFirstUser}, {statusSecondUser}, {metaFirstUser}, {metaSecondUser}')
                embed = discord.Embed(
                    title='Please try again. If this error persists, please contact me via PN.',
                    colour=discord.Colour.red()
                )
                embed.set_author(icon_url=unsuccessfulCheckmark, name='Request Error.')
                embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
                await ctx.send(embed=embed)
    except Exception as err:
        status = responseFirstUser['status']  # Returns error-status
        error = responseFirstUser['error']['message']  # Returns error-message
        embed = discord.Embed(
            title='Request error.',
            description=f'Error: {err}\nStatus: {status}, Error: {error}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='Exception Error.')
        embed.set_footer(text=f'Error occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)


async def get_user_data(accountID, accountName, accountIDTwo, accountNameTwo, ctx):
    try:
        # Variables
        region = 'eu'
        # Fetch all informations
        urlInfoFirstUser = f'https://api.worldoftanks.{region}/wot/account/info/?application_id={WoTAPIKey}&account_id={accountID}'
        responseFirstUser = requests.get(urlInfoFirstUser).json()
        urlInfoSecondUser = f'https://api.worldoftanks.{region}/wot/account/info/?application_id={WoTAPIKey}&account_id={accountIDTwo}'
        responseSecondUser = requests.get(urlInfoSecondUser).json()
        # Listings
        statusFirstUser = responseFirstUser['status']
        metaFirstUser = responseFirstUser['meta']['count']
        statusSecondUser = responseFirstUser['status']
        metaSecondUser = responseFirstUser['meta']['count']
        if statusFirstUser == 'ok' and metaFirstUser == 1 and statusSecondUser == 'ok' and metaSecondUser == 1:  # Request successful and player found
            accountID = f'{accountID}'
            accountIDSecond = f'{accountIDTwo}'
            userName = accountName
            userNameSecond = accountNameTwo
            globalRating = responseFirstUser['data'][accountID]['global_rating']
            lastBattle = datetime.fromtimestamp(responseFirstUser['data'][accountID]['last_battle_time'])

            shots = responseFirstUser['data'][accountID]['statistics']['all']['shots']
            shotsSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['shots']

            battles = responseFirstUser['data'][accountID]['statistics']['all']['battles']
            battlesSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['battles']

            wins = responseFirstUser['data'][accountID]['statistics']['all']['wins']
            winsSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['wins']

            losses = responseFirstUser['data'][accountID]['statistics']['all']['losses']
            lossesSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['losses']

            draws = responseFirstUser['data'][accountID]['statistics']['all']['draws']
            drawsSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['draws']

            frags = responseFirstUser['data'][accountID]['statistics']['all']['frags']
            fragsSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['frags']

            spotted = responseFirstUser['data'][accountID]['statistics']['all']['spotted']
            spottedSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['spotted']

            hits = responseFirstUser['data'][accountID]['statistics']['all']['hits']
            hitsSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['hits']

            maxXP = responseFirstUser['data'][accountID]['statistics']['all']['max_xp']
            maxXPSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['max_xp']

            maxDMG = responseFirstUser['data'][accountID]['statistics']['all']['max_damage']
            maxDMGSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['max_damage']

            maxFrags = responseFirstUser['data'][accountID]['statistics']['all']['max_frags']
            maxFragsSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['max_frags']
            maxFragsTankID = responseFirstUser['data'][accountID]['statistics']['all']['max_frags_tank_id']
            maxFragsTankIDSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['max_frags_tank_id']

            tankingFactor = responseFirstUser['data'][accountID]['statistics']['all']['tanking_factor']
            tankingFactorSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['tanking_factor']

            damage = responseFirstUser['data'][accountID]['statistics']['all']['damage_dealt']
            damageSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['damage_dealt']

            avg_xp = responseFirstUser['data'][accountID]['statistics']['all']['battle_avg_xp']
            avg_xpSecond = responseSecondUser['data'][accountIDSecond]['statistics']['all']['battle_avg_xp']

            lumberjack = responseFirstUser['data'][accountID]['statistics']['trees_cut']
            lumberjackSecond = responseSecondUser['data'][accountIDSecond]['statistics']['trees_cut']

            embed = discord.Embed(
                title=f'__User:__ {userName}  |  __ID:__ {accountID}  |  __Personal Rating:__ {globalRating}\n',
                colour=discord.Colour.green()
            )
            embed.set_author(icon_url=successfulCheckmark, name='Request Successful')
            embed.add_field(
                name=f'__OVERALL STATISTICS:__',
                value=f'Following Statistics were found for **{userName}**:\nhttps://worldoftanks.eu/{language}/community/accounts/{accountID}-{userName}/\n', inline=False,)

            embed.add_field(name='__Battles:__', value=f'```{locale.format_string("%d", battles)} | {locale.format_string("%d", battlesSecond)}```', inline=True)
            embed.add_field(name='__Winrate:__', value=f'```{(wins/battles)*100:.02f}% | {(winsSecond/battlesSecond)*100:.02f}%```', inline=True)
            embed.add_field(name='__Last Battle:__', value=f'```{lastBattle.time()} / {lastBattle.date()}```', inline=True)

            embed.add_field(name='__Wins:__', value=f'```{locale.format_string("%d", wins)} | {locale.format_string("%d", winsSecond)}```', inline=True)
            embed.add_field(name='__Losses:__', value=f'```{locale.format_string("%d", losses)} | {locale.format_string("%d", lossesSecond)}```', inline=True)
            embed.add_field(name='__Draws:__', value=f'```{locale.format_string("%d", draws)} | {locale.format_string("%d", drawsSecond)}```', inline=True)

            embed.add_field(name='__Hits:__', value=f'```{(hits / shots)*100:.02f}% | {(hitsSecond / shotsSecond)*100:.02f}%```', inline=True)
            embed.add_field(name='__Frags:__', value=f'```{locale.format_string("%d", frags)} | {locale.format_string("%d", fragsSecond)}```', inline=True)
            embed.add_field(name='__Spots:__', value=f'```{locale.format_string("%d", spotted)} | {locale.format_string("%d", spottedSecond)}```', inline=True)

            embed.add_field(name='__AVG Battle Experience:__', value=f'```{avg_xp} | {avg_xpSecond}```', inline=True)
            embed.add_field(name='__AVG Battle Damage:__', value=f'```{(damage / battles):.00f} | {(damageSecond / battlesSecond):.00f}```', inline=True)
            embed.add_field(name='__AVG Battle Frags:__', value=f'```{(frags / battles):.02f} | {(fragsSecond / battlesSecond):.02f}```', inline=True)

            embed.add_field(name='__MAX Battle Experience:__', value=f'```{maxXP} | {maxXPSecond}```', inline=True)
            embed.add_field(name='__MAX Battle Damage:__', value=f'```{maxDMG} | {maxDMGSecond}```', inline=True)
            embed.add_field(name='__MAX Battle Frags:__', value=f'```{maxFrags} ({maxFragsTankID}) | {maxFragsSecond} ({maxFragsTankIDSecond})```', inline=True)

            embed.add_field(name='__Tanking Factor:__', value=f'```{tankingFactor} | {tankingFactorSecond}```', inline=True)
            embed.add_field(name='__Lumberjack:__', value=f'```{lumberjack} Trees cut. | {lumberjackSecond} Trees cut.```', inline=True)

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
    except Exception as err:
        status = responseFirstUser['status']  # Returns error-status
        error = responseFirstUser['error']['message']  # Returns error-message
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
    bot.add_command(compare)
