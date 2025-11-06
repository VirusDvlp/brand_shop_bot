import os
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    ORDERS_CHAT_ID: int

    # Google sheets

    SPREADSHEET_NAME: str


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

settings = Settings()

sheet_categories = [
    "BEAUTYGEL",
    "Biogel",
    "LemonBottle",
    "WIQO",
    "НЕОКОЛЛ"
]
