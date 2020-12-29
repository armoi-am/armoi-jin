from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv('TOKEN')
import json
import time
import random

import discord
from discord.ext import commands, tasks

from lib.codeforces.codeforces import CodeForces
from lib.utils.constants import ROLE_NAMES, \
                                REMIND_CHECK_INTERVALS_M, \
                                REQUEST_APPROVED_MESSAGES, \
                                REQUEST_REJECTED_MESSAGES

import asyncio

reminder = commands.Bot(command_prefix='ջին ', cast_insensitive=True)
admin_hub = reminder.get_channel(793160793519816734)

async def send_approved(ctx):
    await ctx.send(random.choice(REQUEST_APPROVED_MESSAGES).format(ctx.message.author.mention))

async def send_rejected(ctx):
    await ctx.send(random.choice(REQUEST_REJECTED_MESSAGES).format(ctx.message.author.mention))

async def warn_admin_hub(func, err, ctx=None):
    await reminder.get_channel(793160793519816734).send(f'''ՄԻ բան էն չի: {err}
Ֆունկցիան՝ {func.name}
{'' if ctx is None else f"""
  Սեռվերը՝ {ctx.guild.name}
  Ալիքը՝ {ctx.channel.name}"""}
''')

async def get_role(guild, role_name):
    if role_name not in [role.name for role in guild.roles]:
        return await guild.create_role(name=role_name)
    else:
        return discord.utils.get(guild.roles, name=role_name)


def is_guild_owner(ctx):
    return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

@reminder.command()
@commands.check_any(commands.is_owner(), commands.check(is_guild_owner))
async def հիշացրու(ctx):
    if ctx.channel not in reminder.channels_to_remind:
        await get_role(ctx.guild, ROLE_NAMES['codeforces'])
        reminder.channels_to_remind.add(ctx.channel)

        with open('./data/channels.json', 'w') as f:
            json.dump([channel.id for channel in reminder.channels_to_remind], f)

    await send_approved(ctx)

@reminder.command()
@commands.check_any(commands.is_owner(), commands.check(is_guild_owner))
async def միՀիշացրու(ctx):
    if ctx.channel in reminder.channels_to_remind:
        reminder.channels_to_remind.remove(ctx.channel)
        with open('./data/channels.json', 'w') as f:
            json.dump([channel.id for channel in reminder.channels_to_remind], f)

    await send_approved(ctx)

@reminder.command()
async def ինձՆշի(ctx):
    role = await get_role(ctx.guild, ROLE_NAMES['codeforces'])
    await ctx.message.author.add_roles(role)
    await ctx.send(random.choice(REQUEST_APPROVED_MESSAGES).format(ctx.message.author.mention))

@reminder.command()
async def ինձՄիՆշի(ctx):
    role = await get_role(ctx.guild, ROLE_NAMES['codeforces'])
    await ctx.message.author.remove_roles(role)
    await send_approved(ctx)

@reminder.command()
async def քոդֆորսիս(channel):
    for contest in CodeForces.get_upcoming():
        await channel.send(embed=contest.embed)

@reminder.command()
@commands.check(lambda ctx: ctx.channel == admin_hub)
async def անջատվի(ctx):
    check_codeforces.cancel()
    if ctx is not None:
        await ctx.send('Անջատվեցի։')

@reminder.command()
@commands.check(lambda ctx: ctx.channel == admin_hub)
async def միացի(ctx):
    check_codeforces.start()
    if ctx is not None:
        await ctx.send('Միացա։')


@reminder.command()
@commands.check(lambda ctx: ctx.channel == admin_hub)
async def ռեստարտ(ctx):
    await send_approved(ctx)
    await անջատվի(ctx)
    await միացի(ctx)

@ռեստարտ.error
async def _ռեստարտ(ctx, error):
    if isinstance(error, commands.errors.CheckAnyFailure):
        await send_rejected(ctx)
    else:
        await ctx.send('Չի ստացվում :/ :')
        await warn_admin_hub(ռեստարտ, error, ctx)

@reminder.event
async def on_ready():
    reminder.channels_to_remind = set()
    with open('./data/channels.json', 'r') as f:
        reminder.channels_to_remind = set([reminder.get_channel(id) for id in json.load(f)])
    for channel in reminder.channels_to_remind:
        await channel.send('Ես կապի մեջ եմ։')

    print('Logged on as', reminder.user)
    check_codeforces.start()

@tasks.loop(seconds=10)
async def check_codeforces():
    print('Checking CodeForces')
    try:
        contests = CodeForces.get_upcoming()

        close_contests = [contest for contest in contests if contest.is_close()]
        if len(close_contests):
            for channel in reminder.channels_to_remind:
                role = await get_role(channel.guild, ROLE_NAMES['codeforces'])
                await channel.send(role.mention)

        for contest in close_contests:
            for channel in reminder.channels_to_remind:
                await channel.send(embed=contest.embed)
    except Exception as err:
        await warn_admin_hub(check_codeforces, err)

reminder.run(TOKEN)
