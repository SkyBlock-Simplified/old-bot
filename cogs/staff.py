from discord.ext import commands

from utils import checks, Embed
from lib import SessionTimeout


class Staff(commands.Cog):
    """
    A collection of tools for the sbs staff to manage the bot.
    """

    emoji = '⚠️'

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.session = bot.http_session

    @commands.command()
    @commands.check_any(commands.is_owner(), checks.is_admin(), checks.is_dev())
    async def disable(self, ctx):
        """
        Use this to disable a command!
        """
        all_commands = self.bot.commands
        enabled_commands = [command for command in all_commands if
                            command.enabled and command.name not in ['disable', 'enable']]
        if not enabled_commands:
            return await ctx.send(f'{ctx.author.mention}, There is no enabled commands to disable!')

        embed = Embed(
            ctx=ctx,
            title='Enter a command from the list below to disable!'
        )
        for command in enabled_commands:
            embed.add_field(
                value=f'```> {command.name}```'
            )
        await embed.send()

        def check(m):
            if m.clean_content.lower() == 'exit':
                raise SessionTimeout
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and not m.clean_content.isdigit()

        _run = True
        while _run:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            for command in enabled_commands:
                if msg.clean_content.lower() == command.name:
                    command.enabled = False
                    await ctx.send(f'{ctx.author.mention}, Successfully disable command `{command.name}`!')
                    _run = False
                    break
            if _run:
                await ctx.send(f'{ctx.author.mention}, Did you make a typo? Choose a command from the list.')

    @commands.command()
    @commands.check_any(commands.is_owner(), checks.is_admin(), checks.is_dev())
    async def enable(self, ctx):
        """
        Use this to enable a command!
        """
        all_commands = self.bot.commands
        disabled_commands = [command for command in all_commands if
                             not command.enabled and command.name not in ['disable', 'enable']]
        if not disabled_commands:
            return await ctx.send(f'{ctx.author.mention}, There is no disabled commands to enable!')

        embed = Embed(
            ctx=ctx,
            title='Enter a command from the list below to enable!'
        )
        for command in disabled_commands:
            embed.add_field(
                value=f'```> {command.name}```'
            )
        await embed.send()

        def check(m):
            if m.clean_content.lower() == 'exit':
                raise SessionTimeout
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and not m.clean_content.isdigit()

        _run = True
        while _run:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            for command in disabled_commands:
                if msg.clean_content.lower() == command.name:
                    command.enabled = True
                    await ctx.send(f'{ctx.author.mention}, Successfully enable command `{command.name}`!')
                    _run = False
                    break
            if _run:
                await ctx.send(f'{ctx.author.mention}, Did you make a typo? Choose a command from the list.')

    @commands.command()
    @commands.check_any(commands.is_owner(), checks.is_admin(), checks.is_dev())
    async def apikey(self, ctx):
        """
        Use this command to check the current api key status.
        """
        pass


def setup(bot):
    bot.add_cog(Staff(bot))