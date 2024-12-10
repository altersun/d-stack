from sanic import Sanic, response, Request, Websocket




def setup_seven_ball(app):
    
    @app.before_server_start
    async def get_answers(app):
        answer_file = 'answers.txt' # TODO: Make dynamic
        answers = []
        try:
            answers += load_answers(answer_file)
        except:
            logger.exception(f"Could not open answer file {answer_file}")
        if len(answers) == 0:
            logger.error('Could not set up set up spritual seven ball, no answers...')
            # TODO: Prevent seven ball from being served if answers don't load
            answers.append("Sorry, I can't read the future today 😔")
        app.ctx.answers = answers

    @app.websocket("/sevenball_answer", name='sevenball_answer')
    async def feed(request: Request, ws: Websocket):
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
                local_answers = copy.deepcopy(app.ctx.answers)
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


    @app.route('/sevenball', name='spritual_seven_ball')
    async def index(request):
        with open('ssb.html') as file:
            return response.html(file.read())