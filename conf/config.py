from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BIND_IP: str
    BIND_PORT: str
    DB_URL: str

    JWT_SECRET_SALT: str
    JWT_EXPIRE: int

    MAIL_USERNAME: str  # название почтового ящика
    MAIL_PASSWORD: str  # пароль от почтового ящика
    MAIL_FROM: str  # название почтового ящика
    MAIL_FROM_NAME: str  # имя, которое будет отображаться в письме (от кого)
    MAIL_PORT: int
    MAIL_SERVER: str

    MERCHANT_LOGIN: str
    PASSWORD1: str
    PASSWORD2: str
    INVOICE_LINK_EXP: int

    LOG_LEVEL: str = 'debug'


settings = Settings()
