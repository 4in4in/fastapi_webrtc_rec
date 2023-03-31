from pydantic import BaseSettings


class Settings(BaseSettings):
    rec_path: str = "./records"
    is_debug: str = True


settings = Settings()
