from common.app.fastapi import FastAPIServer

from service.api.routes import router


def main() -> None:
    server = FastAPIServer(
        router=router,
        host="127.0.0.1",
        port="8000",
    )
    server.run()


if __name__ == "__main__":
    main()
