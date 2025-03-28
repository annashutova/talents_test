from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from conf.config import settings
from webapp.api.invoice.router import invoice_router
from webapp.auth.jwt import JwtTokenT, jwt_auth
from webapp.integrations.mail import mail_client
from webapp.integrations.payment import robokassa
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

    # TODO: сохранить в базе invoice со статусом оплаты

    payment_link = robokassa.generate_open_payment_link(
        out_sum=10,  # сумма для оплаты отчета
        result_url='/example',  # url эндпоинта для подтверждения оплаты
        inv_id=1,  # передается id созданной записи invoice в бд
        description=f'Счет на оплату отчета по тесту {invoice_data.test_id} от {...}',  # TODO: вставить дату выставления счета
        recurring=False,
        email=invoice_data.email if invoice_data.email else user.email,
        expiration_date=datetime.utcnow() + timedelta(minutes=settings.INVOICE_LINK_EXP),
    )

    html = f"""
    <p>Для получения полного отчета перейдите по ссылке оплаты ниже.</p>
    <a href="{payment_link.url}">>>Ссылка на оплату<<</a> 
    <p>После оплаты вы сможете посмотреть отчет по пройденному тесту в личном кабинете.</p> 
    """

    message = MessageSchema(
        subject="Оплата отчета findtalents.ru",
        recipients=[invoice_data.email],
        body=html,
        subtype=MessageType.html
    )

    await mail_client.send_message(message)
    # TODO: вернуть в ответе созданный объект invoice вместо сообщения
    return ORJSONResponse({"message": "email has been sent"}, status_code=status.HTTP_201_CREATED)
