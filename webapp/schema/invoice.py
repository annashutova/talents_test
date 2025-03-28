from datetime import datetime

from pydantic import BaseModel, EmailStr

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
