import logging
import os

import uvicorn
from common.api.exceptions.user import ManagedException
from common.service_logging import LOGGING_CONFIG, configure_logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from service.api.router import router


async def handle_user_already_exists_error(
    _: Request,
    exc: ManagedException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


def main() -> None:
    load_dotenv()

    app = FastAPI()
    app.add_exception_handler(ManagedException, handle_user_already_exists_error)
    host = os.getenv("HOST_IP")
    port = int(os.getenv("HOST_PORT"))

    configure_logging()
    app.include_router(router)

    logging.info("Starting service at http://%s:%s", host, port)

    if app.docs_url:
        logging.info("API docs available at http://%s:%s%s", host, port, app.docs_url)

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_config=LOGGING_CONFIG,
    )


if __name__ == "__main__":
    main()
