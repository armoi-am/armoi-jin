import time
import os

os.environ['TZ'] = 'Asia/Yerevan'
time.tzset()

def duration_str(func):
    def modifier(*args, **kwargs):
        durationSec = func(*args, **kwargs)
        return '%02dժ %02dր' % (durationSec // 3600, (durationSec % 3600) // 60) 
    return modifier

def date_time(func):
    def modifier(*args, **kwargs):
        timeSec = func(*args, **kwargs)
        return time.strftime('%d %b, %H:%M', time.localtime(timeSec))
    return modifier

def hy_month(func):
    dict = {
        'Jan': 'Հունվարի',
        'Feb': 'Փետրվարի',
        'Mar': 'Մարտի',
        'Apr': 'Ապրիլի',
        'May': 'Մայիսի',
        'June': 'Հունիսի',
        'July': 'Հուլիսի',
        'Aug': 'Օգոստոսի',
        'Sept': 'Սեպտեմբերի',
        'Oct': 'Հոկտեմբերի',
        'Nov': 'Նոյեմբերի',
        'Dec': 'Դեկտեմբերի'
    }

    def modifier(*args, **kwargs):
        text = func(*args, **kwargs)
        for key, val in dict.items():
            text = text.replace(key, val)
        return text
    return modifier

