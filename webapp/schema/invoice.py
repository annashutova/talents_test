from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from webapp.models.talents.invoice import InvoiceStatusEnum


class SendInvoiceRequest(BaseModel):
    email: EmailStr | None
    test_id: int


class SendInvoiceResponse(BaseModel):
    id: int
    amount: float
    test_id: int
    status: InvoiceStatusEnum
    created_at: datetime
    updated_at: datetime


class ConfirmInvoiceRequest(BaseModel):
    out_sum: Decimal
    invoice_id: int
    fee: float
    email: EmailStr | str
    signature: str
    payment_method: str
    currency: str
