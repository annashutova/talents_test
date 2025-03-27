from pydantic import BaseModel, EmailStr


class SendInvoiceRequest(BaseModel):
    email: EmailStr | None
    test_id: int


class SendInvoiceResponse(BaseModel):
    message: str
