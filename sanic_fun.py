from sanic import Sanic, response
import asyncio
import websockets
import datetime
from sanic.log import logger

app = Sanic(__name__)

@app.websocket('/time')
async def time(request, ws):
    while True:
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        logger.info(f'WHAT TIME IS IT?? {current_time}')
        await ws.send(current_time)
        await asyncio.sleep(1)

@app.route('/')
async def index(request):
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hello World Sanic Example</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                text-align: center;
                padding: 50px;
            }
            h1 {
                color: #007bff;
            }
            p {
                font-size: 24px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Hello World!</h1>
        <p>This is a simple Sanic example serving a "hello world" webpage.</p>
        <p>Current time: <span id="current-time">Loading...</span></p>
        <script>
            const websocket = new WebSocket('ws://' + window.location.host + '/time');
            const currentTimeElement = document.getElementById('current-time');
            websocket.onmessage = (event) => {
                currentTimeElement.textContent = event.data;
            };
        </script>
    </body>
    </html>
    '''
    return response.html(html_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
