import logging
from typing import Union

from aiogram.bot import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pycoingecko import CoinGeckoAPI

from config import Config, get_config


config: Config = get_config(env_path='.env')
logging.basicConfig(level=config.log_level)

bot = Bot(token=config.bot_token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler(timezone='UTC')
cg = CoinGeckoAPI()


def calculate_percent(first: Union[int, float], second: Union[int, float]) -> Union[int, float]:
    '''Calculate price percent'''
    percent = ((first - second) / ((first + second) / 2)) * 100
    return float('{:.4f}'.format(percent))


async def send_price() -> None:
    '''Send price to telegram'''
    old_price = await dp.storage.get_data(chat='price', user='price')
    now_price = cg.get_price(ids=config.coin_id, vs_currencies=config.vs_currenci)
    if old_price:
        if old_price[config.coin_id][config.vs_currenci] > now_price[config.coin_id][config.vs_currenci]:
            await dp.storage.set_data(chat='price', user='price', data=now_price)
            percent = calculate_percent(
                first=old_price[config.coin_id][config.vs_currenci],
                second=now_price[config.coin_id][config.vs_currenci]
            )
            answer = f'📉 {now_price[config.coin_id][config.vs_currenci]} (-{percent}%)'
            await bot.send_message(chat_id=config.telegram_id, text=answer)
        elif old_price[config.coin_id][config.vs_currenci] < now_price[config.coin_id][config.vs_currenci]:
            await dp.storage.set_data(chat='price', user='price', data=now_price)
            percent = calculate_percent(
                first=now_price[config.coin_id][config.vs_currenci],
                second=old_price[config.coin_id][config.vs_currenci]
            )
            answer = f'📈 {now_price[config.coin_id][config.vs_currenci]} (+{percent}%)'
            await bot.send_message(chat_id=config.telegram_id, text=answer)
    elif not old_price:
        await dp.storage.set_data(chat='price', user='price', data=now_price)


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