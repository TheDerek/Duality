from app.user import WebClient


class RequestError(Exception):
    def __init__(self, message: str, exception_type: str, client: WebClient):
        super().__init__(message)
        self.client = client
        self._exception_type = exception_type

    def get_error_response(self):
        return {
            "error": {
                "type": self._exception_type,
                "user_message": str(self)
            }
        }
