import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_PASS: str
    DB_NAME: str
    DB_USER: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTS: int

    PHONE_NUMBER: int
    PASSWORD: str

    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_IMAGE_TYPE: list = ["image/jpeg",
                                "image/png", "image/webp", "image/svg+xml"]

    @property
    def PRODUCT_DIR(self):
        dir_path = "media/product"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    @property
    def CATEGORY_DIR(self):
        dir_path = "media/category"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    # SQLALCHEMY_DATABASE_URL = f"postgresql://:root@db:5432/fastapi"

    @property
    def SQLALCHEMY_DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
