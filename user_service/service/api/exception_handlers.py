from fastapi import Request
from fastapi.responses import JSONResponse

from service.api.exceptions import (
    ManagedException,
)


async def handle_managed_exception(
    _: Request,
    exc: ManagedException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
