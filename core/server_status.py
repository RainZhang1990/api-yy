from core.config import Config


def get_server_status(server):
    status = Config().server_status.get(server, "")

    return not status, status
