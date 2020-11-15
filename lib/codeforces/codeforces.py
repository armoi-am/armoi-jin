import discord
import requests
import time
import json

from lib.utils.decorators import duration_str, date_time, hy_month
from lib.utils.color_generators import rg_linear_gradient

class Contest():
    def __init__(self, id, name, type, phase, frozen, durationSeconds, startTimeSeconds, relativeTimeSeconds):
        self.__id = id
        self.__name = name
        self.__type = type
        self.__phase = phase
        self.__frozen = frozen
        self.__duration_seconds = durationSeconds
        self.__start_time_seconds = startTimeSeconds
        self.__relative_time_seconds = relativeTimeSeconds

    @property
    @duration_str
    def duration(self):
        return self.__duration_seconds

    @property
    @duration_str
    def before_start(self):
        return -self.__relative_time_seconds

    @property
    def start_time_seconds(self):
        return self.__start_time_seconds

    @property
    @hy_month
    @date_time
    def start_date_time(self):
        return self.__start_time_seconds

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def type(self):
        return self.__type

    def __repr__(self):
        return f'Contest(id={self.__id}, name={self.__name}, type={self.__type}, phase={self.__phase}, frozen={self.__frozen}, duration_seconds={self.__duration_seconds}, start_time_seconds={self.__start_time_seconds}, relative_time_seconds={self.__relative_time_seconds})'

    def is_close(self):
        return -30 * 60 <= self.__relative_time_seconds < -25 * 60
    
    @property
    def embed(self):
        embed = discord.Embed(
            title=self.name,
            url=f'https://codeforces.com/contests/{self.id}',
            color=rg_linear_gradient(0, 3 * 24 * 60 * 60, min(3 * 24 * 60 * 60, -self.__relative_time_seconds))
        )
        embed.add_field(name='Մինչև մեկնարկը', value=self.before_start)
        embed.add_field(name='Մեկնարկը', value=self.start_date_time)
        embed.add_field(name='Տևողությունը', value=self.duration)
        return embed

class CodeForces():

    @staticmethod
    def get_upcoming():
        url = 'https://codeforces.com/api/contest.list'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception as err:
            raise err
        upcoming = sorted([
            Contest(**contest)
            for contest in json.loads(response.content)['result']
            if contest['phase'] == 'BEFORE' and contest['relativeTimeSeconds'] < 0 and contest['relativeTimeSeconds'] > -24 * 7 * 60 * 60
        ], key=lambda x: -x.start_time_seconds)

        return upcoming
    
    @staticmethod
    def message_from_contest_list(contests):
        embed = discord.Embed(
            title='CodeForces Contests',
            url='https://codeforces.com/contests',
            color=0x576fa6,
        )
        for contest in contests:
            embed.add_field(name=contest.name, value=str(contest))
        return embed

if __name__ == '__main__':
    print(CodeForces.get_upcoming())
 