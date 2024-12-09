import aiohttp
from sanic import Sanic, response, Request, Websocket
from sanic.log import logger
import random
import copy
import sys
import io
from PIL import Image

from circle_draw import create_annulus_with_wrapped_text

app = Sanic(__name__)

def png_encode_image(image: Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    png_data = buffer.getvalue()
    buffer.close()
    return png_data

def load_answers(answer_file: str) -> list:
    with open(answer_file) as af:
        answers = [line.rstrip() for line in af]
    return answers

ANSWERS = load_answers('answers.txt')
ANSWER_LOCK = False
SEVEN_BALL_DEFAULT = create_annulus_with_wrapped_text(font_size=80, text='7')
WAIT_FOR_IT = create_annulus_with_wrapped_text(font_size=25, text='Wait for it...')

async def get_random_int(maximum: int, force_local: bool = False) -> int:
    return get_random_ints(maximum, 1, force_local=force_local)[0]

async def get_random_ints(maximum: int, quantity: int = 1, force_local: bool = False) -> list:
    # Request 2 random numbers from random.org based on maximum^2

    if not force_local:
        url_raw = [
            f"https://www.random.org/integers/?num={quantity}",
            f"&min=1&max={maximum}",
            "&col=1&base=10&format=plain&rnd=new",
        ]
        url = ''.join(url_raw)

        logger.info(f'Requesting random number  (1 to {maximum} from {url}')
        async with aiohttp.ClientSession() as session:
           # async with session.get(url) as response:
           response = await session.get(url)
        if response.status == 200:
            try:
                ret_raw = await response.text()
                logger.info(f"Resonse from Random.org: {ret_raw}")
                ret = [int(randint) for randint in ret_raw.split()]
                logger.info(f"Parsed response from Random.org: {ret}")
                return ret
            except:
                logger.error(f"Bad payload {response.text()}")
        else:
            logger.error(f"Bad status code {response.status}")
    
    # If we get here, fall back to psuedorandom
    random.seed()
    backup_ret = [int(random.random() * maximum) for _ in range(quantity)]
    logger.info(f"Supplying psuerandom as a backup: {backup_ret}")
    return backup_ret


@app.websocket("/answer", name='answer')
async def feed(request: Request, ws: Websocket):
    global ANSWERS
    async for msg in ws:
        logger.info(f'Recieved: {msg}')
        if msg == "INITIAL":
            logger.info("Sending initial image")
            encoded_7 = png_encode_image(SEVEN_BALL_DEFAULT)
            await ws.send(encoded_7)
            
        else:    
            # Tell the requester to sit tight
            wait_for_it = png_encode_image(WAIT_FOR_IT)
            await ws.send(wait_for_it)

            # Methodolgy:
            # 1. Make a local copy of the answer list
            # 2. Get two random numbers, 1 to <length of list squared>
            # 3. re-seed local random number generator with first random int
            # 4. Shuffle local list with local randgen
            # 5. Index into shuffled list with second random int mod <length of list>
            local_answers = copy.deepcopy(ANSWERS)
            rand_ints = await get_random_ints(len(local_answers)**2, 2)
            random.seed(rand_ints[0])
            random.shuffle(local_answers)
            index = (rand_ints[1] % len(local_answers)) - 1
            try:
                answer = local_answers[index]
            except:
                logger.exception(f'Bad index {index}')
                answer = "The future remains uncertain..."
            answer_img = png_encode_image(
                create_annulus_with_wrapped_text(text=answer)
            )
            await ws.send(answer_img)
        await ws.send("All done!")


@app.route('/answers', name='main')
async def index(request):
    with open('ssb.html') as file:
        return response.html(file.read())
    

def load_answers(answer_file: str) -> list:
    with open(answer_file) as af:
        answers = [line.rstrip() for line in af]
    return answers


@app.route('/reload', name='reload')
async def reload_answers(answer_file: str):
    # TODO: Redirect to '/answers/' when done
    global ANSWERS
    global ANSWER_LOCK
    if ANSWER_LOCK:
        return
    ANSWER_LOCK = True
    try:
        ANSWERS = load_answers('answers.txt')
    except:
        pass
    finally:
        ANSWER_LOCK = False

    
if __name__ == '__main__':
    logger.info(f'global copy of answers: {ANSWERS}')
    if len(ANSWERS) <= 0:
        logger.error('Could not load answers from answer file!')
        sys.exit(-1)
    app.run(host='0.0.0.0', port=8000)
    
