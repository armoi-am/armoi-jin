from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv('TOKEN')

import discord
import lib.codeforces.codeforces as codeforces

class Reminder(discord.Client):

    PREFIX = 'Վաչո '

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: discord.Message):
        if not message.content.startswith(Reminder.PREFIX):
            return
        msg = message.content[len(Reminder.PREFIX):].split()
        print('Message:', msg)
        if msg[0] == 'քոդֆորսիս':
            channel = message.channel
            await channel.send('\n'.join(['https://codeforces.com/contests'] + [str(contest) for contest in codeforces.CodeForces.get_upcoming()]))

reminder = Reminder()

reminder.run(TOKEN)

