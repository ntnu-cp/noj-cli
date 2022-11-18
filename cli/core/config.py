import os
import json
from pathlib import Path
from typing import Any, Dict
from .context import Context


class Config:
    CONTEXT = 'default'
    API_BASE = 'https://api.noj.tw/'
    curr_user = None

    @classmethod
    def default_context(cls):
        return {'api_base': 'https://api.noj.tw/'}

    @classmethod
    def config_path(cls) -> Path:
        config_root = os.getenv('NOJ_HOME', Path.home() / '.noj')
        config_root = Path(config_root)
        config_root.mkdir(exist_ok=True)
        if not config_root.is_dir():
            raise NotADirectoryError(f'{config_root} is not a directory.')
        return config_root / '.config.json'

    @classmethod
    def load_config_file(cls) -> Dict[str, Any]:
        '''
        Load .config.json
        '''
        config = json.load(cls.config_path().open())
        if type(config) != dict:
            raise TypeError(f'Ivalid config type. It should be a JSON object.')
        return config

    @classmethod
    def load(cls, key: str = CONTEXT) -> None:
        '''
        Load existing context
        '''
        context = Context(key)
        cls.API_BASE = context.api_base
        cls.curr_user = context.login_credential()

    @classmethod
    def add_context(cls, key: str):
        '''
        Write a new context to config file
        '''
        try:
            config = cls.load_config_file()
        except FileNotFoundError:
            config = {}
        if key in config:
            raise ValueError('Duplicated context key.')
        config.update({key: cls.default_context()})
        config_path = cls.config_path()
        json.dump(config, config_path.open('w'))


# Config.add_context('default')