import aiohttp
import random


async def get_random_int(maximum: int, force_local: bool = False) -> int:
    return get_random_ints(maximum, 1, force_local=force_local)[0]


async def get_random_ints(maximum: int, quantity: int = 1, force_local: bool = False) -> list:
    if not force_local:
        url_raw = [
            f"https://www.random.org/integers/?num={quantity}",
            f"&min=1&max={maximum}",
            "&col=1&base=10&format=plain&rnd=new",
        ]
        url = ''.join(url_raw)

        async with aiohttp.ClientSession() as session:
           # async with session.get(url) as response:
           response = await session.get(url)
        if response.status == 200:
            try:
                ret_raw = await response.text()
                ret = [int(randint) for randint in ret_raw.split()]
                return ret
            except:
                # TODO: exception handling
                pass
        else:
            # TODO: Bad response handling
            pass
    
    # If we get here, fall back to psuedorandom
    random.seed()
    backup_ret = [int(random.random() * maximum) for _ in range(quantity)]
    return backup_ret
