import tempfile
import os

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import MessageSchema, MessageType
from starlette import status

from webapp.api.invoice.router import invoice_router
from webapp.crud.invoice import update_invoice_status
from webapp.infrastructure.integrations.google_drive import download_pdf_by_name
from webapp.infrastructure.integrations.payment import robokassa
from webapp.infrastructure.integrations.mail import mail_client
from webapp.db.postgres import get_session
from webapp.infrastructure.middleware.get_form_data import get_invoice_data_from_form
from webapp.logger import logger
from webapp.schema.invoice import ConfirmInvoiceRequest


@invoice_router.post('/confirm')
async def confirm_invoice(
        invoice_data: ConfirmInvoiceRequest = Depends(get_invoice_data_from_form),
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to POST /invoice/confirm')

    result = robokassa.is_result_notification_valid(
        signature=invoice_data.signature,
        out_sum=invoice_data.out_sum,
        inv_id=invoice_data.invoice_id
    )

    if result:
        logger.info(
            'Invoice with id = %d successfully processed',
            invoice_data.invoice_id
        )
        message = f'OK{invoice_data.invoice_id}'
        response_status = status.HTTP_200_OK

        html = f"""
        <p>Оплата прошла успешно!</p>
        <p>Теперь вы можете посмотреть отчет по пройденному тесту в личном кабинете.</p> 
        """
        email = MessageSchema(
            subject="Оплата отчета findtalents.ru",
            recipients=[invoice_data.email],
            body=html,
            subtype=MessageType.html
        )
        await mail_client.send_message(email)

        await update_invoice_status(invoice_data.invoice_id, session)
    else:
        logger.error(
            'Invoice with id = %d Failed',
            invoice_data.invoice_id
        )
        message = 'FAIL'
        response_status = status.HTTP_400_BAD_REQUEST

        html = f"""
        <p>К сожалению, оплата не прошла.</p>
        <p>Попробуйте повторить операцию позже.</p> 
        """
        email = MessageSchema(
            subject="Оплата отчета findtalents.ru",
            recipients=[invoice_data.email],
            body=html,
            subtype=MessageType.html
        )
        await mail_client.send_message(email)

    return ORJSONResponse(message, status_code=response_status)


@invoice_router.post('/confirm/v2')
async def confirm_invoice_v2(
        invoice_data: ConfirmInvoiceRequest = Depends(get_invoice_data_from_form),
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to POST /invoice/confirm/v2')

    result = robokassa.is_result_notification_valid(
        signature=invoice_data.signature,
        out_sum=invoice_data.out_sum,
        inv_id=invoice_data.invoice_id
    )

    if result:
        logger.info(
            'Invoice with id = %d successfully processed',
            invoice_data.invoice_id
        )
        message = f'OK{invoice_data.invoice_id}'
        response_status = status.HTTP_200_OK

        pdf_filename = f"Вася.pdf"

        try:
            pdf_bytes = await download_pdf_by_name(pdf_filename)
        except Exception as e:
            logger.error(f"Failed to download PDF: {e}")
            raise HTTPException(500, "Report not found")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        email = MessageSchema(
            subject="Ваш отчет FindTalents",
            recipients=['annashut@inbox.ru'],
            body="Отчет во вложении",
            attachments=[tmp_path],
            subtype=MessageType.plain,
        )
        await mail_client.send_message(email)
        os.unlink(tmp_path)

        await update_invoice_status(invoice_data.invoice_id, session)
    else:
        logger.error(
            'Invoice with id = %d Failed',
            invoice_data.invoice_id
        )
        message = 'FAIL'
        response_status = status.HTTP_400_BAD_REQUEST

        html = f"""
        <p>К сожалению, оплата не прошла.</p>
        <p>Попробуйте повторить операцию позже.</p> 
        """
        email = MessageSchema(
            subject="Оплата отчета findtalents.ru",
            recipients=['annashut@inbox.ru'],
            body=html,
            subtype=MessageType.html
        )
        await mail_client.send_message(email)

    return ORJSONResponse(message, status_code=response_status)
