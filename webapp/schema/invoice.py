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
    out_sum: float = Field(validation_alias='OutSum')
    invoice_id: int = Field(validation_alias='InvId')
    fee: float = Field(validation_alias='Fee')
    email: EmailStr | None = Field(validation_alias='EMail')
    signature: str = Field(validation_alias='SignatureValue')
    payment_method: str = Field(validation_alias='PaymentMethod')
    currency: str = Field(validation_alias='IncCurrLabel')
