from typing import Any, Dict

from fastapi.responses import ORJSONResponse


def _prepare_response(data: Dict[str, Any]) -> ORJSONResponse:
    return ORJSONResponse(
        {
            'data': data,
        }
    )
