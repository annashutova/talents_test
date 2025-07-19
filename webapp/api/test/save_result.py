import uuid
from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from fastapi_mail import MessageType, MessageSchema
from sqlalchemy.ext.asyncio import AsyncSession

from conf.config import settings
from webapp.api.test.router import test_router
from webapp.auth.password import hash_password
from webapp.crud.invoice import create_invoice
from webapp.crud.user import get_user_by_email, create_user
from webapp.crud.user_answer import balk_insert_answers
from webapp.crud.user_result import post_test_result
from webapp.crud.user_test import post_test
from webapp.db.postgres import get_session
from webapp.infrastructure.integrations.mail import mail_client
from webapp.infrastructure.integrations.payment import robokassa
from webapp.logger import logger
from webapp.models.talents.user import GenderEnum
from webapp.schema.answer import Responses
from webapp.models.talents.user_test import StatusEnum


@test_router.post('/save-response', response_class=ORJSONResponse)
async def answer_question(
        response_data: Responses,
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to POST /tests/save-response')

    # 2. Создаем нового пользователя или получаем id существующего (по email).
    user = await get_user_by_email(session, response_data.email)
    if user is None:
        try:
            user = await create_user(
                {
                    'first_name': response_data.first_name,
                    'last_name': response_data.last_name,
                    'surname': response_data.surname,
                    'email': response_data.email,
                    'password': hash_password(str(uuid.uuid1())),
                    'gender': GenderEnum.male if response_data.gender == 'Мужской' else GenderEnum.female,
                    'date_of_birth': response_data.date_of_birth,
                },
                session,
            )
        except Exception as error:
            logger.error('Error while creating user: %s', str(error))

    # 3. Делаем запись в таблице user_test с новым тестированием.
    test = await post_test(user.id, StatusEnum.finished, session)

    # 4. Записываем ответы пользователя на вопросы в user_answer.
    answers = list(map(lambda x: x.update({'test_id': test.id})), response_data.answers)
    await balk_insert_answers(answers, session)

    # 5. Считаем результаты и записываем в таблицу user_result.
    await post_test_result(test.id, session)

    # 6. Создаем новый платеж в таблице invoice и отправляем пользователю на почту платежную ссылку.
    invoice = await create_invoice(test.id, session)

    payment_link = robokassa.generate_open_payment_link(
        out_sum=invoice.amount,
        result_url=f'https://clever-inherently-earwig.ngrok-free.app/invoice/confirm',
        inv_id=invoice.id,
        description=f'Счет на оплату отчета по тесту {test.id} от {invoice.created_at}',
        recurring=False,
        email=response_data.email,
        expiration_date=datetime.now() + timedelta(minutes=settings.INVOICE_LINK_EXP),
    )

    html = f"""
        <p>Для получения полного отчета перейдите по ссылке оплаты ниже.</p>
        <a href="{payment_link.url}">>>Ссылка на оплату<<</a> 
        <p>После оплаты вам на почту придет отчет с результатами тестирования.</p> 
        """

    message = MessageSchema(
        subject="Оплата отчета findtalents.ru",
        recipients=[response_data.email],
        body=html,
        subtype=MessageType.html
    )

    await mail_client.send_message(message)

    return ORJSONResponse(content={}, status_code=200)
