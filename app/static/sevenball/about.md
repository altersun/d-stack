# Your Future Awaits!
The Spiritual Seven Ball is a prognosticant toy that is kind of an off-brand version of a [well-established classic](https://en.wikipedia.org/wiki/Magic_8_Ball). You hold a yes/no question in your mind or speak it aloud, then shake the ball and view the helpful answer revealed in the viewing window.

## If there's already such a toy, why make a copy?
It's not a copy, it's *off-brand*. But on that theme why make an off-brand version when a few faithful recreations of the real thing already exist online?

Honestly it started with a conversation about random number generation with my wife. And it left me thinking about fun things one could do with a real source of random number generation...and fortunately, [random.org](random.org) exits.

### Methodology
* The seven ball is hosted in a [Sanic](sanic.dev) app
* All images of the seven ball are drawn at time of need by the [Python Imaging Library](https://github.com/python-pillow/Pillow) or "pillow"
* The list of answers is stored on the server as a text file which is loaded at app start
* When a user presses the button asking for an answer to their question, an HTTP request is sent to random.org for a random number. Said random number is used to index into the loaded list of answers. The anwer is then drawn by pillow, the drawing is sent over a websocket, and then rendered as a PNG by the user's browser.
* Because a websocket is used, the work can be done server-side instead of client-side and no further page loads are required

## "Off-brand?"
Yeah since it's not official it can be a bit more rude than the original. Nothing unsafe for work but...don't take the answers too personally.