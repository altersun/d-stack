import aiohttp
import asyncio

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        url_raw = [
            "https://www.random.org/integers/?num=1",
            f"&min=1&max={20}",
            "&col=1&base=10&format=plain&rnd=new",
        ]
        url = ''.join(url_raw)
        print(url)
        async with session.get(url) as response:
            data = await response.text()
            print("Response:", data)

# Run the async function
asyncio.run(fetch_data())
