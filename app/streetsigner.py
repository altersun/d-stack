import io
from PIL import Image
from sanic import Sanic, response, Request, Websocket
from sanic.log import logger

from street_sign_gen import generate_street_sign_raw


STREET_DEFAULT = generate_street_sign_raw("YOUR", "ST")
STREET_BAD = generate_street_sign_raw("OHNOITWENTWRO", "NG")
STREET_WAIT = generate_street_sign_raw("WAITFORIT..", "..")

def png_encode_image(image: Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    png_data = buffer.getvalue()
    buffer.close()
    return png_data


def setup_streetsigner(app):
    
    @app.websocket("/ws/streetsigner", name='ws_streetsigner')
    async def feed(request: Request, ws: Websocket):
        async for msg in ws:
            logger.info(f'Recieved: {msg}')
            if msg == "INITIAL":
                logger.info("Sending initial image")
                encoded_street = png_encode_image(STREET_DEFAULT)
                await ws.send(encoded_street)

            else:    
                # Tell the requester to sit tight
                wait_for_it = png_encode_image(STREET_WAIT)
                await ws.send(wait_for_it)
                try:
                    name, type = msg.rsplit(' ', 1)
                    if len(name) == 0:
                        name = 'EMPTYNAME'
                    street_img = png_encode_image(
                        generate_street_sign_raw(name, type)
                    )
                    await ws.send(street_img)
                    logger.info(f"Sent '{name}' '{type}'")
                except:
                    logger.exception("Sending backup image")
                    await ws.send(png_encode_image(STREET_BAD))
            await ws.send("All done!")
            


    @app.route('/streetsigner', name='streetsigner')
    async def index(request):
        with open('static/streetsigner/streetsigner.html') as file:
            return response.html(file.read())
        
        