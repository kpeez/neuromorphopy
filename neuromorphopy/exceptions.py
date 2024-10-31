class NeuroMorphoError(Exception):
    """Base exception for NeuroMorpho-related errors"""

    pass


class ApiError(NeuroMorphoError):
    """API request errors"""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(f"API Error ({status_code}): {message}")


class ValidationError(NeuroMorphoError):
    """Data validation errors"""

    pass
