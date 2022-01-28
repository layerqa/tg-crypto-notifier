from os import getenv
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config(object):
    bot_token: str
    telegram_id: int
    log_level: str
    interval: int
    coin_id: str
    vs_currenci: str


def get_config(env_path: str) -> Config:
    '''Get config model'''
    load_dotenv(dotenv_path=env_path)
    return Config(
        bot_token=getenv(key='bot_token'),
        telegram_id=int(getenv(key='telegram_id')),
        log_level=getenv(key='log_level'),
        interval=int(getenv(key='interval')),
        coin_id=getenv(key='coin_id'),
        vs_currenci=getenv(key='vs_currenci')
    )