# D-Stack
I wanted to make a simple web app and kind of fell down a rabbit hole. Ended up making an entire website "from scratch," where I managed all the tool installation and setup by myself.

## "From Scratch"
Not technically. I didn't write my own version of Docker and nginx. But I didn't use Squarespace, either (not to knock it, it's a fine service).

## "D" Stack?
My name is David and my first house is on Donnybrook road. **D** seemed like a fit.

## What's the stack?
Good question! 
* nginx (on port 80) runs in a docker container serving static content
* Sanic (python webserver, on port 8000) lives in a second container serving dynamic content and websockets
* nginx proxy forwards requests for dynamic content and websockets to the Sanic app in the second container
* Whole thing runs in Linux, either on my machine for testing or likely a DigitalOcean droplet if on the real internet.

### *Two* containers?
Yeah, I could have just run Sanic by intself but I wanted the power of nginx available if I ever need it. Plus, Sanic can't serve on port 80 without elevated priveledges but nginx can. After doing some reading it seems running each in their own container is more stable than jamming them all into one. Each has their own Dockerfile and both are started together with docker-compose.

### Why Sanic?
Python is my favorite scripting language so a python framework was a no-brainer. Sanic was appealing beacause:
* Easy to learn
* Websocket support

### Why do you want websockets?
Dude why *wouldn't* you want websockets? Dynamic content serice is rad. There's also socket.io but that seems more hefty than anything I can think to make right now would need.

## Where can I check out what's there?
If it's live...welcome to [Donnybrook](http://www.donnybrook.boston)!
