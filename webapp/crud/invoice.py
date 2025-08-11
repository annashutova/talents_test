from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.infrastructure.middleware.metrics import integration_latency
from webapp.models.talents.invoice import Invoice, InvoiceStatusEnum, INVOICE_AMOUNT


@integration_latency
async def create_invoice(test_id: int, session: AsyncSession) -> Invoice:
    logger.info('Creating invoice for test with id = %d.', test_id)
    invoice = (
        await session.scalars(
            insert(Invoice)
            .values(
                amount=INVOICE_AMOUNT,
                test_id=test_id,
                status=InvoiceStatusEnum.not_paid,
            )
            .returning(Invoice)
        )
    ).one_or_none()

    await session.commit()

    return invoice


@integration_latency
async def get_invoice_by_test_id(test_id: int, session: AsyncSession) -> Invoice | None:
    logger.info('Selecting invoice for test with id = %d.', test_id)
    return (
        await session.scalars(
            select(Invoice)
            .where(Invoice.test_id == test_id)
        )
    ).one_or_none()


@integration_latency
async def update_invoice_status(invoice_id: int, session: AsyncSession) -> None:
    logger.info('Updating invoice status with id = %d.', invoice_id)
    await session.execute(
            update(Invoice)
            .where(Invoice.id == invoice_id)
            .values(status=InvoiceStatusEnum.paid)
        )
    await session.commit()


@integration_latency
async def get_test_id_by_invoice_id(invoice_id: int, session: AsyncSession) -> int:
    logger.info('Selecting test_id for invoice with id = %d.', invoice_id)
    return (
        await session.scalars(
            select(Invoice.test_id)
            .where(Invoice.id == invoice_id)
        )
    ).one_or_none()
