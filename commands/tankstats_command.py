import discord
import time
from discord.ext import commands
from datetime import datetime, date

infoCheckmark = 'https://previews.123rf.com/images/vanreeell/vanreeell2101/vanreeell210100291/162736118-.jpg'



# This command is executed after a user send the command "!wots_help" in discord
@commands.command()
async def tankstats(ctx):
    print(f'[{date.today()} at {time.strftime("%H:%M:%S")}] User "{ctx.author}" typed: !wots_help')
    embed = discord.Embed(
        title=f'{ctx.author.name} - Here is a list of all Bot Commands:',
        description="The following Commands are accepted:",
        colour=discord.Colour.from_rgb(240, 204, 46)
    )
    embed.set_author(icon_url=infoCheckmark, name='List of Commands:')
    embed.add_field(name='!wots_help', value='Displays all available commands.', inline=False)
    embed.add_field(name='!stats', value='Displays all the Player stats.\nSyntax: **!stats** YourUserNameHere', inline=False)
    embed.set_footer(text=f'Information created on {date.today()} at {time.strftime("%H:%M:%S")}')
    await ctx.send(f'{ctx.author.mention}', embed=embed)
    #await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(tankstats)

