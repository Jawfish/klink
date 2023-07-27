import logging
import os
from fastapi.responses import JSONResponse

import uvicorn
from common.service_logging import configure_logging, load_default_config_file
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from service.api.router import router
from common.api.exceptions.user import ManagedException

async def handle_user_already_exists_error(_: Request, exc: ManagedException):
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
    log_file = load_default_config_file()


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
