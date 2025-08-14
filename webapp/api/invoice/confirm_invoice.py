import tempfile
import os

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import MessageSchema, MessageType
from starlette import status

from webapp.api.invoice.router import invoice_router
from webapp.crud.invoice import update_invoice_status, get_test_id_by_invoice_id
from webapp.crud.user import get_user_by_test_id
from webapp.crud.user_result import parse_test_result
from webapp.infrastructure.integrations.payment import robokassa
from webapp.infrastructure.integrations.mail import mail_client
from webapp.db.postgres import get_session
from webapp.infrastructure.middleware.get_form_data import get_invoice_data_from_form
from webapp.logger import logger
from webapp.models.talents.user import GenderEnum
from webapp.reports.generate_report import generate_personality_report
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

        try:
            test_id = await get_test_id_by_invoice_id(invoice_data.invoice_id, session)
        except Exception as error:
            logger.error('Error occured while retrieving test id: $s', str(error))
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Report could not be generated")

        try:
            user = await get_user_by_test_id(session, test_id)
        except Exception as error:
            logger.error('Error occured while retrieving user: $s', str(error))
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Report could not be generated")

        try:
            await update_invoice_status(invoice_data.invoice_id, session)
        except Exception as error:
            logger.error("Failed to update invoice status: %s", str(error))
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Report could not be generated")

        try:
            report_data = await parse_test_result(test_id, session)
        except Exception as error:
            logger.error('Error occured while retrieving test results for report: $s', str(error))
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Report could not be generated")
        report_data['name'] = f'{user.last_name} {user.first_name} {user.surname if user.surname else ""}'
        report_data['gender'] = 'Женский' if user.gender == GenderEnum.female else 'Мужской'
        report_data['date_of_birth'] = user.date_of_birth

        try:
            pdf_bytes = generate_personality_report(report_data)
        except Exception as error:
            logger.error(f"Failed to generate PDF: {str(error)}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Report could not be generated")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        email = MessageSchema(
            subject="Ваш отчет FindTalents",
            recipients=[invoice_data.email],
            body="Спасибо, что воспользовались нашим сервисом! Можете посмотреть свой отчет во вложении.",
            attachments=[tmp_path],
            subtype=MessageType.plain,
        )
        await mail_client.send_message(email)
        os.unlink(tmp_path)
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
