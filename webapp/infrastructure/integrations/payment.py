import hashlib
from datetime import datetime, timedelta
from urllib import parse

from robokassa import HashAlgorithm, Robokassa

from conf.config import settings


ROBOKASSA_PAYMENT_URL = 'https://auth.robokassa.ru/Merchant/Index.aspx'


robokassa = Robokassa(
    merchant_login=settings.MERCHANT_LOGIN,
    password1=settings.TEST_PASSWORD1,
    password2=settings.TEST_PASSWORD2,
    algorithm=HashAlgorithm.md5,
    is_test=False,
)


def generate_signature(login: str, out_sum: float, inv_id: int, password: str):
    signature_str = f"{login}:{out_sum}:{inv_id}:{password}"
    return hashlib.md5(signature_str.encode()).hexdigest()


def generate_payment_link(out_sum: float, invoice_id: int, test_id: int, user_email: str):
    signature = generate_signature(
        settings.MERCHANT_LOGIN,
        out_sum,
        invoice_id,
        settings.TEST_PASSWORD1
    )

    data = {
        'MerchantLogin': settings.MERCHANT_LOGIN,
        'OutSum': out_sum,
        'InvId': invoice_id,
        'Description': f'Счет на оплату отчета по тесту {test_id}',
        'ExpirationDate': datetime.now() + timedelta(minutes=settings.INVOICE_LINK_EXP),
        'Email': user_email,
        'SignatureValue': signature,
        'IsTest': 0
    }

    return f'{ROBOKASSA_PAYMENT_URL}?{parse.urlencode(data)}'
