from unittest.mock import Mock

from QuantDataAPI.client import QuantDataAPI_Client


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.headers = {}
        self.text = ""

    def json(self):
        return self._payload


def client_with_payload(
    payload,
    *,
    output_type="json",
    timezone="America/New_York",
    status_code=200,
):
    client = QuantDataAPI_Client(
        "test-key",
        output_type=output_type,
        timezone=timezone,
    )
    client._session.post = Mock(
        return_value=FakeResponse(payload, status_code=status_code)
    )
    return client
