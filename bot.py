from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv('TOKEN')

import discord
from discord.ext import commands, tasks

from lib.codeforces import codeforces as _codeforces

import asyncio

reminder = commands.Bot(command_prefix=';;')

@reminder.command()
async def remind_here(channel):
    if channel not in reminder.channels_to_remind:
        reminder.channels_to_remind.add(channel)
        await channel.channel.send('Channel added!')
    else:
        await channel.channel.send('Already set to remind!')

@reminder.command()
async def stop_reminding(channel):
    if channel in reminder.channels_to_remind:
        reminder.channels_to_remind.remove(channel)
    await channel.send('Ok. I will not remind here.')

@reminder.command()
async def codeforces(channel):
    for contest in _codeforces.CodeForces.get_upcoming():
        await channel.send(embed=contest.embed)


@reminder.event
async def on_ready():
    reminder.channels_to_remind = set()
    print('Logged on as', reminder.user)
    check_codeforces.start()

@tasks.loop(minutes=5)
async def check_codeforces():
    print('Checking CodeForces')
    contests = codeforces.CodeForces.get_upcoming()

    close_contests = [contest for contest in contests if contest.is_close()]

    for contest in close_contests:
        print(contest)
        asyncio.gather(*[
            channel.send(embed=contest.embed)
            for channel in reminder.channels_to_remind
        ])

reminder.run(TOKEN)
