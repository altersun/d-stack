import asyncio
from dataclasses import dataclass
from multiprocessing import Manager
import os
from sanic import Sanic, response, Request, Websocket
from sanic.log import logger
import socket
import random_dot_org as rdo
import time
from typing import AsyncGenerator


SPATH = './guession_data_mgr.uds'

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


async def manage_session_store(storage):
    timeout = 600 # Clean things up every 10 minutes
    while True:
        await asyncio.sleep(timeout)
        for id, data in storage:
            if data.last_access < time.time() - timeout:
                del storage[id]


async def session_key_generator():
    # TODO: More elegent key generation
    key = 1
    while True:
        key += 1
        yield key


async def data_store_client_handler(storage, keygen, reader, writer):
    try:
        data = await reader.read(32)
        message = data.decode()
        logger.info(f"Received: {message}")
        response = ""

        # Format: key {lower|higher|correct}
        # Special format: 0 {maximum}
        rcvd = message.split()
        key = int(rcvd[0])

        # Return: key {guess|0}
        # The 0 is if the guessing is finished
        if key == 0:
            newkey = await anext(keygen)
            guesser = guess_generator(int(rcvd[1]))
            guess = await anext(guesser)
            storage[newkey] = SessionData(guesser, time.time())
            response = f"{key} {guess}"
        else:
            to_send = [f"{key}",]
            result = rcvd[1]
            try:
                guess = await storage[key].generator.asend(result)
                to_send.append(f"{guess}")
            except StopIteration:
                to_send.append("0")
                del storage[key]
            response = " ".join(to_send)
  
        writer.write(response.encode())
        await writer.drain()
        logger.info(f"Sent: {response}")
    except Exception as e:
        logger.exception(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()




async def data_store_client_handler(storage, keygen, reader, writer):
    try:
        data = await reader.read(32)
        message = data.decode()
        logger.info(f"Received: {message}")
        response = ""

        # Format: key {lower|higher|correct}
        # Special format: 0 {maximum}
        rcvd = message.split()
        key = int(rcvd[0])

        # Return: key {guess|0}
        # The 0 is if the guessing is finished
        if key == 0:
            newkey = await anext(keygen)
            guesser = guess_generator(int(rcvd[1]))
            guess = await anext(guesser)
            storage[newkey] = SessionData(guesser, time.time())
            response = f"{key} {guess}"
        else:
            to_send = [f"{key}",]
            result = rcvd[1]
            try:
                guess = await storage[key].generator.asend(result)
                to_send.append(f"{guess}")
            except StopIteration:
                to_send.append("0")
                del storage[key]
            response = " ".join(to_send)
  
        writer.write(response.encode())
        await writer.drain()
        logger.info(f"Sent: {response}")
    except Exception as e:
        logger.exception(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

 
def setup_guessie(app):
    storage = Manager()

    @app.before_server_start
    async def set_multiprocessing(app, loop):
        try:
            set_start_method("fork", force=True)
        except RuntimeError:
            pass  # Already set, ignore
    
        if not is_socket_in_use(SPATH):
            data_store_process = Process(
                target=run_data_store_server, 
                kwargs={'socket_path': SPATH}
            )
            data_store_process.start()
            logger.info("Guessie server started")

    @app.websocket("/ws/guessie/<number:int>")
    async def guessdriver(request: Request, ws: Websocket, number: int):
        async for msg in ws:
            logger.info(f"guessie received {msg}")
            if msg == "START":
                request_string = f"0 {number}"
            else:
                request_string = msg.rstrip()
            logger.info(f"guessie requesting: {request_string}")
            response = await ask_guessie(request_string, SPATH)
            logger.info(f"guessie said: {response}")
            await ws.send(response)
            await ws.close()
    
    @app.route("/guessie/<number:int>", name="guessie_specific")
    async def guessserver(request, number):
        with open("static/guessie/guessie.html") as file:
            return response.html(file.read())

    @app.route("/guessie", name="guessie_generic")
    async def guessserver_g(request):
        return await guessserver(request, number=100)
    
    @app.before_server_stop
    async def guessie_teardown():
        if os.path.exits(SPATH):
            os.remove(SPATH)
        

if __name__ == '__main__':
    asyncio.run(test())

