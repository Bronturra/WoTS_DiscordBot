from os import listdir
from os.path import isfile, join
import discord
from discord.ext import commands


# DiscordBot Class for custom DiscordBot
class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    # This function is executed after the program started and bot is loaded
    async def on_ready(self):
        print('[WoTS] Bot is online.')
        print('[WoTS] Bot is listed on ' + str(len(bot.guilds)) + ' Servers.')
        print('---------------------')
        await bot.change_presence(status=discord.Status.online, activity=discord.Game('!help'))

    # This function is executed after a user tries to execute an unknown command
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(
            colour=discord.Colour.red()
        )
        embed.set_author(icon_url=unsuccessfulCheckmark, name=f'Error: {error}')
        await ctx.send(embed=embed)


# Variables
unsuccessfulCheckmark = 'https://thumbs.dreamstime.com/b/check-marks-red-cross-icon-simple-vector-illustration-140098693.jpg'
bot = DiscordBot(command_prefix='!')

# Read DiscordToken from File when Script starts
with open("Tokens/DiscordToken.txt") as f:
    # Read DiscordToken from File
    discordToken = f.read().rstrip("\n")
    f.close()


# Add all available commands to current Bot
if __name__ == '__main__':
    path = 'commands'
    commands = [f for f in listdir(path) if isfile(join(path, f))]
    for command in commands:
        try:
            bot.load_extension(f'{path}.{command[:-3]}')
        except Exception as exc:
            print(f'Failed to load file {command}')

bot.remove_command('help')  # Removes the default !help command
bot.run(discordToken)
# await ctx.send(f'Possible Finding: {userName} : {userID}')
# !stats silverfox_77
