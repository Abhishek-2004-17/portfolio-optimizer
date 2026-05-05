from fastapi import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class ValidationError(HTTPException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=422, detail=detail)


class ExternalAPIError(HTTPException):
    def __init__(self, detail: str = "External API error"):
        super().__init__(status_code=502, detail=detail)
