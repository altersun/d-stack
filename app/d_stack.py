
from sanic import Sanic
from sanic.log import logger

from guessie import setup_guessie
from sevenball import setup_sevenball
from streetsigner import setup_streetsigner


def init():
    
    app = Sanic("D-Stack")
    setup_guessie(app)
    setup_sevenball(app)
    setup_streetsigner(app)
    return app


if __name__ == '__main__':
    init().run()
    logger.info("We D-stackin")
       
