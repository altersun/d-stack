from sanic import Sanic, response, Request, Websocket
from sanic.log import logger

from sevenball import setup_sevenball


def init():
    app = Sanic("D-Stack")
    setup_sevenball(app)
    return app


if __name__ == '__main__':
    from sanic import app as sanic_app
    sanic_app.run(init)
    logger.info("We D-stackin")
       
