from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv('TOKEN')
DATABASE_URL=os.getenv('DATABASE_URL')
DATABASE_ROW = 'testing_channels' if os.getenv('MODE') == 'TESTING' else 'channels'
import json
import time
import random

import discord
from discord.ext import commands, tasks

from lib.codeforces.codeforces import CodeForces
from lib.utils.constants import ROLE_NAMES, \
                                REMIND_CHECK_INTERVALS_M, \
                                REQUEST_APPROVED_MESSAGES, \
                                REQUEST_REJECTED_MESSAGES, \
                                ADMIN_HUB_ID

import asyncio

import psycopg2

db_conn = psycopg2.connect(DATABASE_URL)

db_cur = db_conn.cursor()


reminder = commands.Bot(command_prefix='ջին ')

async def reply_approved(ctx: commands.Context):
    emoji = random.choice([
        '👍',
        '👌',
        '✌️'
    ])
    await ctx.message.add_reaction(emoji)
    await ctx.send(random.choice(REQUEST_APPROVED_MESSAGES).format(ctx.message.author.mention))

async def reply_rejected(ctx):
    emoji = random.choice([
        '😠',
        '💢',
        '😠',
        '😾'
    ])
    await ctx.message.add_reaction(emoji)
    await ctx.send(random.choice(REQUEST_REJECTED_MESSAGES).format(ctx.message.author.mention))

async def get_role(guild, role_name):
    if role_name not in [role.name for role in guild.roles]:
        return await guild.create_role(name=role_name, color=discord.Colour.dark_magenta())
    else:
        return discord.utils.get(guild.roles, name=role_name)


@reminder.command()
@commands.has_permissions(administrator=True)
async def հիշացրու(ctx):
    if ctx.channel not in reminder.channels_to_remind:
        await get_role(ctx.guild, ROLE_NAMES['codeforces'])
        reminder.channels_to_remind.add(ctx.channel)
        db_cur.execute(f'INSERT INTO {DATABASE_ROW} (channel_id) VALUES(%s)', (ctx.channel.id, ))
        db_conn.commit()

    await reply_approved(ctx)

@reminder.command()
@commands.has_permissions(administrator=True)
async def միՀիշացրու(ctx):
    if ctx.channel in reminder.channels_to_remind:
        reminder.channels_to_remind.remove(ctx.channel)
        db_cur.execute(f'DELETE FROM {DATABASE_ROW} WHERE channel_id = %s', (ctx.channel.id, ))
        db_conn.commit()

    await reply_approved(ctx)

@reminder.command()
async def ինձՆշի(ctx):
    role = await get_role(ctx.guild, ROLE_NAMES['codeforces'])
    await ctx.message.author.add_roles(role)
    await reply_approved(ctx)

@reminder.command()
async def ինձՄիՆշի(ctx):
    role = await get_role(ctx.guild, ROLE_NAMES['codeforces'])
    await ctx.message.author.remove_roles(role)
    await reply_approved(ctx)

@reminder.command()
async def քոդֆորսիս(ctx, arg=''):
    if arg == 'լրիվ':
        await ctx.send(embed=CodeForces.one_embed())
    else:
        for contest in CodeForces.get_upcoming():
            await ctx.send(embed=contest.embed)

@reminder.command()
@commands.check(lambda ctx: ctx.channel.id == ADMIN_HUB_ID)
async def անջատվի(ctx):
    check_codeforces.cancel()
    if ctx is not None:
        await ctx.send('Անջատվեցի։')

@reminder.command()
@commands.check(lambda ctx: ctx.channel.id == ADMIN_HUB_ID)
async def միացի(ctx):
    check_codeforces.start()
    if ctx is not None:
        await ctx.send('Միացա։')


@reminder.command()
@commands.check(lambda ctx: ctx.channel.id == ADMIN_HUB_ID)
async def ռեստարտ(ctx):
    await reply_approved(ctx)
    await անջատվի(ctx)
    await միացի(ctx)


async def warn_admin_hub(ctx, error):
    await reminder.get_channel(ADMIN_HUB_ID).send(f'''ՄԻ բան էն չի: {error}
{'' if ctx is None else f"""
Ֆունկցիան՝ {ctx.command.name}
> Սեռվերը՝ {ctx.guild.name}
> Ալիքը՝ {ctx.channel.name}"""}
''')

@անջատվի.error
@միացի.error
@ռեստարտ.error
@քոդֆորսիս.error
@հիշացրու.error
@միՀիշացրու.error
@ինձՆշի.error
@ինձՄիՆշի.error
async def էռոր(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await reply_rejected(ctx)
    else:
        await ctx.send('Չի ստացվում <:confused:793616226352889856> :')
        await warn_admin_hub(ctx, error)

@reminder.event
async def on_ready():
    reminder.channels_to_remind = set()
    db_cur.execute(f'SELECT * FROM {DATABASE_ROW};')
    reminder.channels_to_remind = set([reminder.get_channel(id[0]) for id in db_cur.fetchall()])

    print('Logged on as', reminder.user)
    check_codeforces.start()

@tasks.loop(minutes=REMIND_CHECK_INTERVALS_M['codeforces'])
async def check_codeforces():
    print('Checking CodeForces')
    try:
        contests = CodeForces.get_upcoming()

        close_contests = [
            contest
            for contest in contests
            if contest.is_close() or contest.will_be_close_in_a_day()
        ]
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
