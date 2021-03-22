import ast
import logging
import operator as op
import traceback
from asyncio import sleep

from discord import FFmpegPCMAudio, VoiceClient
from discord.channel import VoiceChannel
from discord.ext import commands
from discord.ext.commands import Cog, Context

from coc_scraper import get_troops, match_name, get_cost, create_table, chunkify, get_buildings, minimize_string

logger = logging.getLogger(__name__)


class General(Cog):
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
                 ast.USub: op.neg, }

    @commands.command()
    async def cost(self, ctx: Context, *, unit_name: str = None):
        """
        Return cost of each level of unit, building or spell scraped from clashofclans.fandom.com.
        It also includes values such as hitpoints, damage per second, damage per attack and other values in the
        main table.

        :param ctx:
        :param unit_name:
        :return:
        """
        logger.info(f"Fetching cost for {unit_name}")
        try:
            troops = get_troops()
            buildings = get_buildings()
            troops_buildings = {**troops, **buildings}
            name = match_name(unit_name, list(troops_buildings.keys()))
            if name:
                link = troops_buildings[name]
                logger.info(f"Fetching url {link}")
                header, rows = get_cost(link)
                if len(" ".join(header)) > 120:
                    header = list(map(minimize_string, header))
                for chunk in chunkify(rows, 10):
                    chunk.insert(0, header)
                    await ctx.channel.send("```" +
                                           create_table(chunk) +
                                           "```")
            else:
                await ctx.channel.send("```No matching army or building found.```")
        except:
            traceback.print_exc()
            await ctx.channel.send("```No matching army or building found.```")

    @commands.command(name="ml")
    async def missing_letters(self, ctx: Context, *, words: str = None):
        if not words:
            await ctx.channel.send("```Please enter some words.```")
        else:
            await ctx.channel.send(
                f"```missing letters {list(set('abcdefghijklmnopqrstuvwxyz') - set(words.lower()))}```")

    @commands.command()
    async def bark(self, ctx: Context):
        """
        Enters the users voice channel and plays the bark sound and leaves.
        :param ctx:
        :return:
        """
        voice = ctx.author.voice
        if voice:
            channel: VoiceChannel = voice.channel
            voice_client: VoiceClient = await channel.connect()
            audio_source = FFmpegPCMAudio('dog_bark.mp3')
            if not voice_client.is_playing():
                voice_client.play(audio_source, after=None)
            while voice_client.is_playing():
                await sleep(1)
            await voice_client.disconnect()
        else:
            await ctx.channel.send("```Join a Voice Channel first```")

    def eval(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self.eval(node.left), self.eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self.eval(node.operand))
        else:
            raise TypeError(node)

    @commands.command(name="=")
    async def cal(self, ctx: Context, *, expression: str):
        try:
            await ctx.channel.send(f"```{self.eval(ast.parse(expression, mode='eval').body)}```")
        except:
            await ctx.channel.send(f"```Unsupported expression```")
