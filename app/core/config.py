import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVER_HOST: str = "http://127.0.0.1:8000"
    DB_HOST: str
    DB_PORT: int
    DB_PASS: str
    DB_NAME: str
    DB_USER: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTS: int
    BOT_TOKEN: str
    WEBHOOK_URL: str
    PHONE_NUMBER: int = Field(..., description="Phone number with 998 prefix and 9 digits")
    PASSWORD: str
    OWNER_ID: int
    CHANNEL_ID: int
    MAX_FILE_SIZE: int = Field(5 * 1024 * 1024, ge=1 * 1024 * 1024)  # Min 1 MB, default 5 MB
    ALLOWED_IMAGE_TYPE: list[str] = ["image/jpeg", "image/png", "image/webp", "image/svg+xml"]

    @property
    def PRODUCT_DIR(self) -> str:
        return self._create_directory("media/product")

    @property
    def CATEGORY_DIR(self) -> str:
        return self._create_directory("media/category")

    def _create_directory(self, dir_path: str) -> str:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
