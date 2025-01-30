import os
from dotenv import load_dotenv

class ConfigAdapter:
    def __init__(self) -> None:
        env = dict(os.environ.items())

        # Load default environment variables from .env file
        load_dotenv()
        self._env = dict(os.environ.items())

        # Update environment variables with env
        self._env.update(env)

    def get_config(self, key):
        return self._env.get(key)
