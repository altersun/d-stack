from sanic import Sanic
from sanic.log import logger

from guessy import setup_guessy
from sevenball import setup_sevenball
from streetsigner import setup_streetsigner


def init():
    app = Sanic("D-Stack")
    setup_guessy(app)
    setup_sevenball(app)
    setup_streetsigner(app)
    return app


if __name__ == '__main__':
    from sanic import app as sanic_app
    sanic_app.run(init)
    logger.info("We D-stackin")
       
