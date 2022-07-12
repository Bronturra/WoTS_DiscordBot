# TODO: Implement the Tank specific stats in overall stats
# TODO: Statistics for more modes / random battles is default!
# TODO: Region Request in Command
# TODO: Change the Bot Settings in DiscordBot Webpage
# TODO: Compare the WoT-Armory Stats with DiscordBot stats to set a bigger focus on important stats
# TODO: "Test" Exceptions and Errors
# TODO: Clean up Code, Simplify things, create Classes, Reduce redundant Code
# TODO: Find better Icons
# TODO: Language Support GER/ENG
# TODO: GIT ReadMe
# TODO: Match Details of current match
# TODO: DATABASE INTEGRATION

from os import listdir
from os.path import isfile, join
import discord
import time
from discord.ext import commands
from datetime import datetime, date

# Read DiscordToken from File when Script starts
with open("Tokens/DiscordToken.txt") as f:
    discordToken = f.read().rstrip("\n")
    f.close()

# Global variables
DiscordToken = discordToken
unsuccessfulCheckmark = 'https://thumbs.dreamstime.com/b/check-marks-red-cross-icon-simple-vector-illustration-140098693.jpg'


# DiscordBot Class for own DiscordBot
class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    # This function is executed after the program started to execute and is loaded
    async def on_ready(self):
        print('[WoTS] Bot is online.')
        print('[WoTS] Bot is listed on ' + str(len(bot.guilds)) + ' Servers.')
        print('---------------------')
        await bot.change_presence(status=discord.Status.online, activity=discord.Game('!wots_help'))

    # This function is executed after a user tries to execute an unknown command
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(
            title=f'Error: {error}',
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name='Command not found.')
        embed.set_footer(text=f'Problem occurred on {date.today()} at {time.strftime("%H:%M:%S")}')
        await ctx.send(embed=embed)
        # await ctx.send(f'Error: {error}')


bot = DiscordBot(command_prefix='!')
if __name__ == '__main__':
    path = 'commands'
    commands = [f for f in listdir(path) if isfile(join(path, f))]
    for command in commands:
        try:
            bot.load_extension(f'{path}.{command[:-3]}')
        except Exception as exc:
            print(f'Failed to load file {command}')


bot.run(DiscordToken)
# await ctx.send(f'Possible Finding: {userName} : {userID}')
