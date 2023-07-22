import logging
import os

import uvicorn
from common.service_logging import configure_logging, load_default_config_file
from dotenv import load_dotenv
from fastapi import FastAPI

from service.api.router import router


def main() -> None:
    app = FastAPI()
    host = os.getenv("HOST_IP")
    port = int(os.getenv("HOST_PORT"))
    log_file = load_default_config_file()

    load_dotenv()

    configure_logging(log_file)
    app.include_router(router)

    logging.info("Starting service at http://%s:%s", host, port)

    if app.docs_url:
        logging.info("API docs available at http://%s:%s%s", host, port, app.docs_url)

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_config=log_file,
    )


if __name__ == "__main__":
    main()
