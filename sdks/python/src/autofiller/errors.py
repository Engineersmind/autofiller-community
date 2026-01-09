"""Error classes for the Autofiller SDK."""


class AutofillerError(Exception):
    """Base exception for Autofiller SDK errors."""

    def __init__(self, message: str, code: str = "unknown_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class AuthenticationError(AutofillerError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message, "authentication_error")


class ValidationError(AutofillerError):
    """Raised when request validation fails (400, 422)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "validation_error")


class RateLimitError(AutofillerError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, "rate_limit_exceeded")


class ExtractionError(AutofillerError):
    """Raised when document extraction fails."""

    def __init__(self, message: str, code: str = "extraction_failed") -> None:
        super().__init__(message, code)


class TimeoutError(AutofillerError):
    """Raised when a request or job times out."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, "timeout")
