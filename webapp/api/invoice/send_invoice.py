from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.invoice.router import invoice_router
from webapp.auth.jwt import JwtTokenT, jwt_auth
from webapp.integrations.mail import mail_client
from webapp.crud.user_test import get_user_test_by_id
from webapp.crud.user import get_user_by_id
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.models.talents.user_test import StatusEnum
from webapp.schema.invoice import SendInvoiceRequest, SendInvoiceResponse


@invoice_router.post('/send', response_model=SendInvoiceResponse)
async def send_invoice_by_email(
        invoice_data: SendInvoiceRequest,
        session: AsyncSession = Depends(get_session),
        access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    logger.info('Request to POST /invoice/send')

    user = await get_user_by_id(session, access_token['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id={access_token["user_id"]} not found'
        )

    test = await get_user_test_by_id(invoice_data.test_id, session)
    if test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Test with id={invoice_data.test_id} not found'
        )

    # Validate if test belongs to user that makes the request
    if test.user_id != access_token['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You cannot access this test'
        )

    if test.status != StatusEnum.finished:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Test with id={invoice_data.test_id} is not finished yet.'
        )

    # TODO: сгенерировать ссылку на оплату теста с test_id
    # TODO: отправить сгенерированную ссылку на оплату на почту клиента: invoice_data.email | user.email
    # TODO: сохранить в базе invoice со статусом оплаты

    html = """
    <p>Для получения полного отчета перейдите по ссылке оплаты.</p>
    <p>link</p> 
    <p>После оплаты вы сможете посмотреть отчет по пройденному тесту в личном кабинете.</p> 
    """

    message = MessageSchema(
        subject="Оплата отчета findtalents.ru",
        recipients=[invoice_data.email],
        body=html,
        subtype=MessageType.html
    )

    await mail_client.send_message(message)
    return ORJSONResponse({"message": "email has been sent"}, status_code=status.HTTP_201_CREATED)
