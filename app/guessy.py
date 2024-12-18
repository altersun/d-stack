import asyncio
from collections import namedtuple
from sanic import Sanic, response, Request, Websocket
from sanic.log import logger
import random_dot_org as rdo
import time

SessionData = namedtuple('SessionData', ['generator', 'last_access'])


async def guess_generator(maximum: int) -> int:
    bottom = 1
    top = maximum
    while True: 
        unequal =  bottom != top
        print(f"Bottom: {bottom} Top: {top}")
        guess = await rdo.get_random_int(top, bottom) if unequal else top
        response = yield guess
        if response == 'higher':
            bottom = (guess + 1) if unequal else bottom
        if response == 'lower':
            top = guess - 1 if unequal else top
        if response == 'correct':
            break

async def test():
    import sys
    guesser = guess_generator(10)
    guess = await anext(guesser)
    print(f"I guess {guess}")
    for line_raw in sys.stdin:
        line = line_raw.rstrip()
        if line not in ['higher', 'lower', 'correct']:
            print("Invalid response")
            continue
        try:
            guess = await guesser.asend(line)
            print(f"I guess {guess}")
        except StopAsyncIteration:
            break


async def manage_session_store(app):
    timeout = 300
    while True:
        await asyncio.sleep(timeout)
        for id, data in app.ctx.guession_store.items():
            if data.last_access() < time.time() - timeout():
                del app.ctx.guession_store[id]
        

def setup_guessy(app):

    @app.before_server_start
    async def setup_session_store(app, loop):
        app.ctx.gession_store = {}
        loop.create_task(manage_session_store(app))

    @app.websocket("/ws/guess/<number:int>")
    async def guessdriver(request: Request, ws: Websocket, number: int):
        async for msg in ws:
            logger.info(f"Guessy received {msg}")
            if msg == "START":
                pass
            key, cmd = msg.split()
            if key not in app.ctx.guession_store:
                await ws.send("Invalid session key {key}")
                ws.close()
                return
            if cmd not in ['higher', 'lower', 'correct']:
                await ws.send("Invalid command {key}")
                ws.close ()   
                return
            app.ctx.guession_store[key].last_access = time.time()
            guesser = app.ctx.guession_store[key].generator
            try:
                next_guess = await guesser.asend(cmd)
            except StopAsyncIteration:
                pass



if __name__ == '__main__':
    asyncio.run(test())

