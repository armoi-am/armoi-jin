from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv('TOKEN')

import discord
from discord.ext import tasks

from lib.codeforces import codeforces

class Reminder(discord.Client):

    PREFIX = ';;'

    # TODO: try to move this to CodeForces
    @tasks.loop(minutes=5)
    async def check_codeforces(self):
        channel = self.get_channel(776878413075447828)
        print('Checking CodeForces')
        contests = codeforces.CodeForces.get_upcoming()
        if any([contest.is_close() for contest in contests]):
            await channel.send('<@&777265466808074251>')
            close_contests = [contest for contest in contests if contest.is_close()]
            for contest in close_contests:
                await channel.send(embed=contest.embed)

    async def on_ready(self):
        print('Logged on as', self.user)
        self.check_codeforces.start()

    async def on_message(self, message: discord.Message):
        if not message.content.startswith(Reminder.PREFIX):
            return
        msg = message.content[len(Reminder.PREFIX):].split()
        print('Message:', msg)
        if msg[0] == 'codeforces':
            for contest in codeforces.CodeForces.get_upcoming():
                await message.channel.send(embed=contest.embed)

reminder = Reminder()

reminder.run(TOKEN)

