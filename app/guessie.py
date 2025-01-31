import asyncio
from dataclasses import dataclass
from multiprocessing import Process
import os
from sanic import Sanic, response, Request, Websocket
from sanic.log import logger
import socket
import random_dot_org as rdo
import time
from typing import AsyncGenerator


@dataclass
class SessionData:
    generator: AsyncGenerator
    last_access: float


# Check if socket is in use
def is_socket_in_use(path :str) -> bool:
    return \
        os.path.exists(path) and \
        socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).connect_ex(path) == 0


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


async def data_store_server(socket_path: str):
    storage = {}
    keygen = session_key_generator()
    server = await asyncio.start_unix_server(
        lambda r, w: data_store_client_handler(storage, keygen, r, w),
        path=socket_path
    )
    logger.info(f"Server listening on {socket_path}")
    asyncio.create_task(manage_session_store(storage))
    async with server:
        await server.serve_forever()


async def ask_guessie(msg: str, path: str) -> str:
    reader, writer = await asyncio.open_unix_connection(path)
    writer.write(msg.encode())
    await writer.drain()
    response = await reader.read(32)
    writer.close()
    await writer.wait_closed()
    return response.decode()

 
def setup_guessie(app):
    spath = './guession_data_mgr.uds'
    if not is_socket_in_use(spath):
        data_store_process = Process(
            target=data_store_server, 
            daemon = True,
            kwargs={'socket_path': spath}
        )

    @app.websocket("/ws/guessie/<number:int>")
    async def guessdriver(request: Request, ws: Websocket, number: int):
        async for msg in ws:
            logger.info(f"guessie received {msg}")
            if msg == "START":
                request_string = f"0 {number}"
            else:
                request_string = msg.rstrip()
            logger.info(f"guessie requesting: {request_string}")
            response = await ask_guessie(request_string)
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
        data_store_process.terminate()
        

if __name__ == '__main__':
    asyncio.run(test())

