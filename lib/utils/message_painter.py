from functools import wraps

def coroutine_initializer(fun):
    @wraps(fun)
    def replacement(*args, **kwargs):
        gen = fun(*args, **kwargs)
        gen.send(None)
        return gen
    return replacement

@coroutine_initializer
def paint():
    colors = [
        '',
        'fix'
    ]
    s = yield
    while True:
        for c in colors:
            s = yield f'''```{c}
{s}
```'''

painter = paint()
