# Your Street Sign Awaits!
Since I named my domain after the street I lived on, I figured a street sign graphic on the website would be appropriate. So I went looking for a street sign image generator online, but everything I found online either required some kind of log-in or didn't have any templates *remotely* resembling my local street signs. So...I made my own,

## From scratch??
Kind of...honestly the image generator at the core of this is based on the [Python Image Library (or PILlow)](https://github.com/python-pillow/Pillow) and from a script generated based on ChatGPT scripts. My **bespoke** contributions are doing all the python, docker, and nginx glue to make the image generation available via a website. 

Having worked on the [Spritual Seven Ball](http://www.donnybrook.boston/sevenball) already helped a lot, since in the process I learned how to serve image content via websockets.

### Methodology
* The Streetsigner is hosted in a [Sanic](sanic.dev) app
* All street signs are drawn at time of request by the server via the [Python Imaging Library](https://github.com/python-pillow/Pillow)
* The client's browser and the server use a websocket for requests and sending images. Because a websocket is used, the work can be done server-side instead of client-side and no further page loads are required.
