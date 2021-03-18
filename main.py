import datetime
import logging
import os

import discord
import requests_cache
from discord.ext import commands
from dotenv import load_dotenv

from general import General

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
requests_cache.install_cache('cache')
bot = commands.Bot(command_prefix="!", description="Some basic COC utilities", case_insensitive=True)


@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(
        name="Clash Of Clans",
        type=discord.ActivityType.playing,
        start=datetime.datetime.utcnow()
    ))


if __name__ == '__main__':
    bot.add_cog(General())
    logger.info(f"Starting COC BOT at {datetime.datetime.today().strftime('%d-%b-%Y %I:%M %p')}")
    bot.run(os.getenv('DISCORD_TOKEN'))
