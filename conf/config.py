from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BIND_IP: str
    BIND_PORT: str
    DB_URL: str

    JWT_SECRET_SALT: str
    JWT_EXPIRE: int

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_PORT: int
    MAIL_SERVER: str

    LOG_LEVEL: str = 'debug'


settings = Settings()
