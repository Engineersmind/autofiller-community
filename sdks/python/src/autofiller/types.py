"""Type definitions for the Autofiller SDK."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Union

from pydantic import BaseModel, Field


# Input types
FileInput = Union[str, Path, bytes, BinaryIO]


class ExtractOptions(BaseModel):
    """Options for document extraction."""

    file: Any = Field(exclude=True)
    """Path to file, bytes, or file-like object."""

    filename: str | None = None
    """Optional filename (required when file is bytes or file-like)."""

    domain_pack: str | None = None
    """Domain pack to use. If omitted, auto-routing selects the best pack."""

    include_confidence: bool = True
    """Include confidence scores for each extracted field."""

    include_bounding_boxes: bool = False
    """Include bounding box coordinates for each field."""

    language: str = "en"
    """Document language hint (ISO 639-1 code)."""

    webhook_url: str | None = None
    """Webhook URL for async extraction notifications."""


class BoundingBox(BaseModel):
    """Bounding box coordinates for an extracted field."""

    page: int
    """Page number (1-indexed)."""

    x: float
    """X coordinate (normalized 0-1)."""

    y: float
    """Y coordinate (normalized 0-1)."""

    width: float
    """Width (normalized 0-1)."""

    height: float
    """Height (normalized 0-1)."""


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process."""

    pages: int = 0
    """Total pages in the document."""

    processing_time_ms: int = 0
    """Processing time in milliseconds."""

    model_version: str = "unknown"
    """Model version used for extraction."""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when extraction was created."""


class ExtractResult(BaseModel):
    """Result of a document extraction."""

    id: str
    """Unique extraction ID."""

    status: str
    """Extraction status: 'completed' or 'partial'."""

    domain_pack: str
    """Domain pack used for extraction."""

    data: dict[str, Any]
    """Extracted structured data."""

    confidence: dict[str, float] | None = None
    """Per-field confidence scores (0-1)."""

    bounding_boxes: dict[str, BoundingBox] | None = None
    """Per-field bounding box coordinates."""

    metadata: ExtractionMetadata = Field(default_factory=ExtractionMetadata)
    """Extraction metadata."""

    warnings: list[str] | None = None
    """Non-fatal warnings encountered during extraction."""


class JobStatus(BaseModel):
    """Status of an async extraction job."""

    job_id: str
    """Job ID."""

    status: str
    """Current status: 'pending', 'processing', 'completed', or 'failed'."""

    progress: float | None = None
    """Processing progress (0-100)."""

    result: ExtractResult | None = None
    """Extraction result (when completed)."""

    error: dict[str, str] | None = None
    """Error details (when failed)."""

    created_at: datetime = Field(default_factory=datetime.now)
    """Job creation timestamp."""

    completed_at: datetime | None = None
    """Job completion timestamp."""


class DomainPack(BaseModel):
    """Domain pack information."""

    name: str
    """Pack name/identifier."""

    version: str
    """Pack version."""

    description: str
    """Human-readable description."""

    schema_: dict[str, Any] = Field(alias="schema")
    """JSON Schema for extracted data."""

    routing: dict[str, list[str]] | None = None
    """Routing configuration (keywords, anchors)."""

    supported_formats: list[str] | None = None
    """Supported file formats."""


class HealthStatus(BaseModel):
    """API health status."""

    status: str
    """Health status: 'healthy', 'degraded', or 'unhealthy'."""

    version: str
    """API version."""

    timestamp: datetime = Field(default_factory=datetime.now)
    """Timestamp of health check."""
