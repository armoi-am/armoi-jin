import time

def duration_str(func):
    def modifier(*args, **kwargs):
        durationSec = func(*args, **kwargs)
        return '%02d:%02d' % (durationSec // 3600, (durationSec % 3600) // 60) 
    return modifier

def date_time(func):
    def modifier(*args, **kwargs):
        timeSec = func(*args, **kwargs)
        return time.strftime('%d/%b/%Y %H:%M', time.localtime(timeSec))
    return modifier

def hy_month(func):
    dict = {
        'Jan': 'Հունվ',
        'Feb': 'Փետ',
        'Mar': 'Մարտ',
        'Apr': 'Ապ',
        'May': 'Մայ',
        'June': 'Հուն',
        'July': 'Հուլ',
        'Aug': 'Օգ',
        'Sept': 'Սեպտ',
        'Oct': 'Հոկտ',
        'Nov': 'Նոյ',
        'Dec': 'Դեկտ'
    }

    def modifier(*args, **kwargs):
        text = func(*args, **kwargs)
        for key, val in dict.items():
            text = text.replace(key, val)
        return text
    return modifier

