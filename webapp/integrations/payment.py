from robokassa import HashAlgorithm, Robokassa

from conf.config import settings

robokassa = Robokassa(
    merchant_login=settings.MERCHANT_LOGIN,
    password1=settings.PASSWORD1,
    password2=settings.PASSWORD2,
    algorithm=HashAlgorithm.md5,
    is_test=True,
)

