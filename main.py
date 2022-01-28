import logging

from aiogram.bot import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_polling

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pycoingecko import CoinGeckoAPI

from config import Config, get_config


config: Config = get_config(env_path='.env')
logging.basicConfig(level=config.log_level)

bot = Bot(token=config.bot_token)
dp = Dispatcher(bot=bot)
scheduler = AsyncIOScheduler(timezone='UTC')
cg = CoinGeckoAPI()


async def send_price() -> None:
    '''Send price to telegram'''
    price = cg.get_price(ids=config.coin_id, vs_currencies=config.vs_currenci)
    await bot.send_message(chat_id=config.telegram_id, text=str(price[config.coin_id][config.vs_currenci]))


async def on_bot_start(dp: Dispatcher) -> None:
    '''On bot start up'''
    scheduler.add_job(send_price, trigger='interval', seconds=config.interval)
    scheduler.start()


async def on_bot_stop(dp: Dispatcher) -> None:
    '''On bot shutdown'''
    scheduler.shutdown()


if __name__ == '__main__':
    start_polling(
        dispatcher=dp, skip_updates=True,
        on_startup=on_bot_start, on_shutdown=on_bot_stop
    )