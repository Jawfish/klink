import logging

from service.app.server import run, setup


def main() -> None:
    try:
        app, host, port, log_config = setup()
        run(app, host, port, log_config)
    except Exception:
        logging.exception("An error occurred while setting up and running the server.")
        raise


if __name__ == "__main__":
    main()
