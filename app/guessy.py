import asyncio
from dataclasses import dataclass
from multiprocessing import Process
import os
from sanic import Sanic, response, Request, Websocket
from sanic.log import logger
import random_dot_org as rdo
import time
from typing import AsyncGenerator


@dataclass
class SessionData:
    generator: AsyncGenerator
    last_access: float






async def guess_generator(maximum: int):
    bottom = 1
    top = maximum
    while True: 
        unequal =  bottom != top
        print(f"Bottom: {bottom} Top: {top}")
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


async def manage_session_store(app):
    timeout = 300
    while app.ctx.guession_store is not None:
        await asyncio.sleep(timeout)
        for id, data in app.ctx.guession_store.items():
            if data.last_access < time.time() - timeout:
                del app.ctx.guession_store[id]


async def generate_session_key(app):
    # TODO: More elegent key generation
    key = 1
    while app.ctx.guession_store is not None: # TODO: this doesn't work as intended
        while key in app.ctx.guession_store:
            key += 1
        yield key


async def data_store_client_handler(reader, writer):
    try:
        data = await reader.read(100)
        message = data.decode()
        logger.info(f"Received: {message}")
        
        response = f"Echo: {message}"
        writer.write(response.encode())
        await writer.drain()
        logger.info(f"Sent: {response}")
    except Exception as e:
        logger.exception(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def data_store_server(socket_path: str):
    # Remove the socket file if it exists
    if os.path.exists(socket_path):
        os.remove(socket_path)

    server = await asyncio.start_unix_server(data_store_client_handler, path=socket_path)
    logger.info(f"Server listening on {socket_path}")
    async with server:
        await server.serve_forever()


def setup_guessy(app):
    spath = './guession_data_mgr.uds'
    data_store_process = Process(target=data_store_server, kwargs={'socket_path': spath})

    @app.before_server_start
    async def setup_session_store(app, loop):
        data_store_process.start()
        app.ctx.guession_store = {}
        app.ctx.guession_keygen = generate_session_key(app)
        loop.create_task(manage_session_store(app))

    @app.websocket("/ws/guessy/<number:int>")
    async def guessdriver(request: Request, ws: Websocket, number: int):
        async for msg in ws:
            logger.info(f"Guessy received {msg}")
            if msg == "START":
                guesser = guess_generator(number)
                guess = await anext(guesser)
                key = await anext(app.ctx.guession_keygen)
                app.ctx.guession_store[key] = SessionData(guesser, time.time())
                send_string = f"{key} {guess}"
                logger.info(f"Guessy sending: {send_string}")
                await ws.send(send_string)
                continue
            key_raw, cmd = msg.split()
            key = int(key_raw)
            if key not in app.ctx.guession_store:
                await ws.send(f"Invalid session key {key}")
                logger.info(f"Bad key request: {key}. Available keys: {app.ctx.guession_store.keys()}")
                await ws.close()
                continue
            if cmd not in ['higher', 'lower', 'correct']:
                await ws.send(f"Invalid command {cmd}")
                await ws.close()   
                continue
            app.ctx.guession_store[key].last_access = time.time()
            guesser = app.ctx.guession_store[key].generator
            try:
                next_guess = await guesser.asend(cmd)
                send_string = f"{key} {next_guess}"
                logger.info(f"Guessy sending: {send_string}")
                await ws.send(send_string)
                await ws.close()
            except StopAsyncIteration:
                # User has stated the guess was correct. Clean things up.
                del app.ctx.guession_store[key]

    
    @app.route("/guessy/<number:int>", name="guessy_specific")
    async def guessserver(request, number):
        with open("static/guessy/guessy.html") as file:
            return response.html(file.read())

    @app.route("/guessy", name="guessy_generic")
    async def guessserver_g(request):
        return await guessserver(request, number=100)
    
    @app.main_process_stop
    async def guessy_teardown():
        data_store_process.terminate()
        

if __name__ == '__main__':
    asyncio.run(test())

