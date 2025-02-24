import os
import telegram
import asyncio
from dotenv import load_dotenv

# bot api 호출
env_path = os.path.join(os.path.dirname(__file__),"teleapi_key/.env")
load_dotenv(env_path)

# 메인 로직
async def main():
    token = os.getenv("tele_api")
    bot = telegram.Bot(token)
    await bot.send_message(chat_id = "-4595812781", text = "hello")
    

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())