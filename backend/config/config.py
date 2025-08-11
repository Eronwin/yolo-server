import os.path
import secrets
from typing import Optional, List

from pydantic_settings import BaseSettings

_config = None


class Config(BaseSettings):

    # Common options
    debug: bool = False
    data_dir: Optional[str] = None

    # Server options
    host: Optional[str] = "0.0.0.0"
    port: Optional[int] = None
    database_url: Optional[str] = None
    jwt_secret_key: Optional[str] = None
    system_reserved: Optional[dict] = None
    disable_openapi_docs: bool = False
    enable_cors: bool = True
    allow_origins: Optional[List[str]] = ["*"]
    allow_credentials: bool = True
    allow_methods: Optional[List[str]] = ["GET", "POST"]
    allow_headers: Optional[List[str]] = ["Authorization", "Content-Type"]

    def __init__(self, **values):
        super().__init__(**values)

        # common options
        if self.data_dir is None:
            self.data_dir = self.get_data_dir()

        self.prepare_jwt_secret_key()

        # server options
        self.init_database_url()

        if self.system_reserved is None:
            self.system_reserved = {"ram": 2, "vram": 1}

        self.make_dirs()

    def prepare_jwt_secret_key(self):
        if self.jwt_secret_key is not None:
            return

        key_path = os.path.join(self.data_dir, "jwt_secret_key")
        if os.path.exists(key_path):
            with open(key_path, "r") as file:
                key = file.read().strip()
        else:
            key = secrets.token_hex(32)
            os.makedirs(self.data_dir, exist_ok=True)
            with open(key_path, "w") as file:
                file.write(key)
        self.jwt_secret_key = key

    def init_database_url(self):
        if self.database_url is None:
            self.database_url = f"sqlite:///{self.data_dir}/database.db"
            return

        if (
            not self.database_url.startswith("sqlite://")
            and not self.database_url.startswith("postgresql://")
            and not self.database_url.startswith("mysql://")
        ):
            raise Exception(
                "Unsupported database scheme. Supported databases are sqlite, postgresql, and mysql."
            )

    def make_dirs(self):
        os.makedirs(self.data_dir, exist_ok=True)

    @staticmethod
    def get_data_dir():
        app_name = "python-server-init"
        if os.name == "nt":
            data_dir = os.path.join(os.environ["APPDATA"], app_name)
        elif os.name == "posix":
            data_dir = f"./data/var/lib/{app_name}"
        else:
            raise Exception("Unsupported OS")

        return os.path.abspath(data_dir)


def get_global_config() -> Config:
    return _config


def set_global_config(cfg: Config) -> None:
    global _config
    _config = cfg
    return cfg
