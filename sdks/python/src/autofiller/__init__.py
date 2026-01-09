"""
Autofiller SDK for Python

Official client library for the Autofiller Community Edition API.

Example:
    >>> from autofiller import AutofillerClient
    >>> 
    >>> client = AutofillerClient(api_key="your-api-key")
    >>> result = client.extract(
    ...     file="./invoice.pdf",
    ...     domain_pack="invoice-standard"
    ... )
    >>> print(result.data)
"""

from autofiller.client import AutofillerClient, AsyncAutofillerClient
from autofiller.types import (
    ExtractOptions,
    ExtractResult,
    ExtractionMetadata,
    BoundingBox,
    JobStatus,
    DomainPack,
    HealthStatus,
)
from autofiller.errors import (
    AutofillerError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    ExtractionError,
)

__version__ = "0.1.0"

__all__ = [
    # Clients
    "AutofillerClient",
    "AsyncAutofillerClient",
    # Types
    "ExtractOptions",
    "ExtractResult",
    "ExtractionMetadata",
    "BoundingBox",
    "JobStatus",
    "DomainPack",
    "HealthStatus",
    # Errors
    "AutofillerError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "ExtractionError",
]
