from fastapi.responses import ORJSONResponse

from webapp.api.system.router import system_router
from webapp.logger import logger
from webapp.schema.health import HealthResponse


@system_router.get(
    '/health',
    response_model=HealthResponse,
)
async def health_check() -> ORJSONResponse:
    logger.info('Response to /health')
    return ORJSONResponse(
        {
            'status': 'healthy',
        }
    )
