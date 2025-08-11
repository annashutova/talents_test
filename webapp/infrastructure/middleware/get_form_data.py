from decimal import Decimal

from fastapi import Form
from pydantic import EmailStr

from conf.config import settings
from webapp.schema.invoice import ConfirmInvoiceRequest


async def get_invoice_data_from_form(
    out_sum: Decimal = Form(..., alias='OutSum'),
    invoice_id: int = Form(..., alias='InvId'),
    fee: float = Form(..., alias='Fee'),
    email: EmailStr | str = Form(settings.TEST_EMAIL, alias='EMail'),
    signature: str = Form(..., alias='SignatureValue'),
    payment_method: str = Form(..., alias='PaymentMethod'),
    currency: str = Form(..., alias='IncCurrLabel'),
) -> ConfirmInvoiceRequest:
    return ConfirmInvoiceRequest(
        out_sum=out_sum,
        invoice_id=invoice_id,
        fee=fee,
        email=email,
        signature=signature,
        payment_method=payment_method,
        currency=currency
    )
