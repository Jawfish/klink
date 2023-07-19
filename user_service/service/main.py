from common.app.fastapi import FastAPIServer

from service.api.routes import router

server = FastAPIServer(
    router=router,
    host="0.0.0.0",
    port="8001",
)


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
