import asyncio
import json
from sanic import Sanic, response, Request, Websocket
from sanic.log import logger
import random_dot_org as rdo


async def guess_generator(maximum: int):
    bottom = 1
    top = maximum
    while True: 
        unequal =  bottom != top
        logger.info(f"Bottom: {bottom} Top: {top}")
        guess = await rdo.get_random_int(top, bottom) if unequal else top
        guess = 1 if guess < 1 else guess
        response = yield guess
        if response == 'higher':
            bottom = (guess + 1) if unequal else bottom
        if response == 'lower':
            top = guess - 1 if unequal else top
            
        if response == 'correct':
            break
        logger.info(f"Bottom {bottom} Top {top}")


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

 
def setup_guessie(app):

    @app.before_server_start
    async def before(app):
        pass
        # in case I need it

    @app.websocket("/ws/guessie_guess", name='guessie_guess')
    async def guessdriver(request: Request, ws: Websocket):
        async for msg in ws:
            try:
                loaded = json.loads(msg)
            except ValueError: 
                logger.exception(f"Improperly formatted message recieved: {msg}")
                continue
            logger.info(f"guessie received {loaded}")
            try:
                if loaded['correct'] == True:
                    response = "Yaay!"
                else:
                    request_string = msg.rstrip()
                    logger.info(f"guessie requesting: {request_string}")
                    response_raw = await rdo.get_random_int( \
                                    loaded['high'], loaded['low']) \
                                    if loaded['high'] != loaded['low'] \
                                    else loaded['high']
                    response = str(response_raw)
                    logger.info(f"guessie said: {response}")
            except KeyError: 
                logger.exception("Message must have fields 'high', 'low', and 'correct'")
            await ws.send(response)

    @app.route("/guessie/<upper:strorempty>", name="guessie_specific")
    async def guessserver(request, upper):
        with open("static/guessie/guessie.html") as file:
            return response.html(file.read())

    @app.route("/guessie", name="guessie_generic")
    async def guessserver_g(request):
        return await guessserver(request, upper="100")

        

if __name__ == '__main__':
    asyncio.run(test())

