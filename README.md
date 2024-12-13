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

## Technical Details

### Docker
```
├── .dockerignore
├── Makefile
├── docker-compose.yaml
├── app
|   ├── requirements.txt
│   ├── static
|   |   └── ...
|   └── ...
├── nginx
│   ├── Dockerfile
│   └── nginx.conf
└── sanic
    └── Dockerfile
```
* nginx and sanic each have their own Dockerfiles
  * nginx container:
    * nginx's config file is added to the container upon build
    * Exposes port 80 as the host machine's port 80
    * nginx listens on port 80
  * Sanic container:
    * The Python requirements.txt is added to the container upon build
    * Uses pip to install python dependencies from the requirements.txt file
    * Installs other dependencies via apt
    * Exposes port 8000 as the host's machines's port 8000
    * Sanic is started in production mode referencing scripts in the app directory
    * The Sanic app listens on port 8000
* Both Dockerfiles are reference in the docker-compose.yaml file
  * The whole system can be started in the background with `docker-compose up --detach`

### nginx
* nginx is confured to serve static content itself
  * nginx has a location rule that uses regex so that any URL /URL serves app/static/URL.html
  * TH\here is another rule for /URL/about to serve a page that describes the app of that page.
    * The "about.html" is generatated from markdown by Python-markdown (I am not good at html yet)
* Dynamic content is proxy forwarded to the Sanic container
  * There is a specifc rule for websockets: /ws/URL is forwarded to the Sanic container
    * ...by forwarding it to port 8000 of the host machine

### Sanic
* Started in production mode with multiple workers
  * Because of the production mode start, all app init functions must use the decorators `main_process_start`, `before_server_start`, or `after_server_start`
  * Any app can be added to the server by the creation of an app-specific init function which uses the decorators above and others like `route` and `websocket` then calling that init function from the generalized init function in d-stack.py.
