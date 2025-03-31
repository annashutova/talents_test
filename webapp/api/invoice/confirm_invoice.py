from fastapi import Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.invoice.router import invoice_router
from webapp.crud.invoice import update_invoice_status
from webapp.integrations.payment import robokassa
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.invoice import ConfirmInvoiceRequest


@invoice_router.post('/confirm')
async def confirm_invoice(
        invoice_data: ConfirmInvoiceRequest,
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to POST /invoice/confirm')

    result = robokassa.is_result_notification_valid(
        signature=invoice_data.signature,
        out_sum=invoice_data.out_sum,
        inv_id=invoice_data.invoice_id
    )

    if result:
        logger.info('Invoice with id = %d successfully processed', invoice_data.invoice_id)
        message = f'OK{invoice_data.invoice_id}'
        response_status = status.HTTP_200_OK

        await update_invoice_status(invoice_data.invoice_id, session)
    else:
        logger.error('Invoice with id = %d Failed', invoice_data.invoice_id)
        message = 'FAIL'
        response_status = status.HTTP_400_BAD_REQUEST
    return ORJSONResponse(message, status_code=response_status)
