from typing import Dict


class Context:

    def __init__(self, key: str) -> None:
        from .config import Config
        try:
            context = Config.load_config_file()[key]
        except KeyError:
            raise ValueError(f'context \'{key}\' not found.')
        try:
            self.api_base = context['api_base']
            self.username = context['username']
            self.password = context['password']
        except KeyError:
            raise ValueError('Invalid context value.')

    def login_credential(self) -> Dict[str, str]:
        return {
            'username': self.username,
            'password': self.password,
        }
