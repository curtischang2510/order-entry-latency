import logging

import requests

logger = logging.getLogger(__name__)


def log_exchange_response_headers(response: requests.Response, *args, **kwargs) -> None:
    if response.request.path_url == "/exchange":
        logger.info(
            "Exchange HTTP response status=%d headers=%s",
            response.status_code,
            dict(response.headers),
        )
