import logging
import os

import uvicorn
from common.service_logging import configure_logging, LOGGING_CONFIG
from dotenv import load_dotenv
from fastapi import FastAPI

from service.api.router import router


def main() -> None:
    load_dotenv()

    app = FastAPI()
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
