"""Autofiller API clients (sync and async)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, BinaryIO

import httpx

from autofiller.errors import (
    AuthenticationError,
    AutofillerError,
    ExtractionError,
    RateLimitError,
    ValidationError,
)
from autofiller.types import (
    DomainPack,
    ExtractResult,
    ExtractionMetadata,
    HealthStatus,
    JobStatus,
)

DEFAULT_BASE_URL = "https://api.autofiller.dev/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


class AutofillerClient:
    """
    Synchronous client for the Autofiller API.

    Example:
        >>> client = AutofillerClient(api_key="your-api-key")
        >>> result = client.extract(
        ...     file="./invoice.pdf",
        ...     domain_pack="invoice-standard"
        ... )
        >>> print(result.data)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """
        Initialize the Autofiller client.

        Args:
            api_key: Your Autofiller API key.
            base_url: API base URL (for self-hosted instances).
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        if not api_key:
            raise ValidationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def __enter__(self) -> "AutofillerClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def health(self) -> HealthStatus:
        """
        Check API health status.

        Returns:
            HealthStatus with current API status.
        """
        response = self._client.get("/health")
        self._handle_response(response)
        data = response.json()
        return HealthStatus(**data)

    def extract(
        self,
        file: str | Path | bytes | BinaryIO,
        *,
        filename: str | None = None,
        domain_pack: str | None = None,
        include_confidence: bool = True,
        include_bounding_boxes: bool = False,
        language: str = "en",
    ) -> ExtractResult:
        """
        Extract data from a document (synchronous).

        Use this for small documents (<10 pages). For larger documents,
        use `extract_async()`.

        Args:
            file: Path to file, bytes, or file-like object.
            filename: Optional filename (required when file is bytes).
            domain_pack: Domain pack to use. If omitted, auto-routing is used.
            include_confidence: Include confidence scores.
            include_bounding_boxes: Include bounding box coordinates.
            language: Document language hint (ISO 639-1).

        Returns:
            ExtractResult with extracted data.
        """
        files, data = self._prepare_multipart(
            file=file,
            filename=filename,
            domain_pack=domain_pack,
            include_confidence=include_confidence,
            include_bounding_boxes=include_bounding_boxes,
            language=language,
        )

        response = self._client.post("/extract", files=files, data=data)
        self._handle_response(response)
        return self._parse_extract_result(response.json())

    def extract_async(
        self,
        file: str | Path | bytes | BinaryIO,
        *,
        filename: str | None = None,
        domain_pack: str | None = None,
        webhook_url: str | None = None,
        include_confidence: bool = True,
        include_bounding_boxes: bool = False,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Start an async extraction job.

        Args:
            file: Path to file, bytes, or file-like object.
            filename: Optional filename.
            domain_pack: Domain pack to use.
            webhook_url: URL to POST results when complete.
            include_confidence: Include confidence scores.
            include_bounding_boxes: Include bounding boxes.
            language: Document language hint.

        Returns:
            Dict with job_id, status, and estimated_time_seconds.
        """
        files, data = self._prepare_multipart(
            file=file,
            filename=filename,
            domain_pack=domain_pack,
            include_confidence=include_confidence,
            include_bounding_boxes=include_bounding_boxes,
            language=language,
        )

        if webhook_url:
            data["webhook_url"] = webhook_url

        response = self._client.post("/extract/async", files=files, data=data)
        self._handle_response(response)
        return response.json()

    def get_job(self, job_id: str) -> JobStatus:
        """
        Get status of an async extraction job.

        Args:
            job_id: Job ID from extract_async().

        Returns:
            JobStatus with current status and result if complete.
        """
        response = self._client.get(f"/jobs/{job_id}")
        self._handle_response(response)
        data = response.json()

        # Convert nested result if present
        if data.get("result"):
            data["result"] = self._parse_extract_result(data["result"])

        return JobStatus(**data)

    def wait_for_job(
        self,
        job_id: str,
        *,
        poll_interval: float = 2.0,
        max_wait: float = 300.0,
    ) -> ExtractResult:
        """
        Wait for an async job to complete.

        Args:
            job_id: Job ID to wait for.
            poll_interval: Seconds between status checks.
            max_wait: Maximum seconds to wait.

        Returns:
            ExtractResult when job completes.

        Raises:
            ExtractionError: If job fails.
            TimeoutError: If max_wait is exceeded.
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            job = self.get_job(job_id)

            if job.status == "completed" and job.result:
                return job.result

            if job.status == "failed":
                error_msg = job.error.get("message", "Job failed") if job.error else "Job failed"
                error_code = job.error.get("code", "job_failed") if job.error else "job_failed"
                raise ExtractionError(error_msg, error_code)

            time.sleep(poll_interval)

        raise AutofillerError("Job timed out waiting for completion", "job_timeout")

    def list_domain_packs(self) -> list[DomainPack]:
        """
        List all available domain packs.

        Returns:
            List of DomainPack objects.
        """
        response = self._client.get("/domain-packs")
        self._handle_response(response)
        data = response.json()
        return [DomainPack(**pack) for pack in data.get("items", [])]

    def get_domain_pack(self, pack_name: str) -> DomainPack:
        """
        Get details for a specific domain pack.

        Args:
            pack_name: Name of the domain pack.

        Returns:
            DomainPack with schema and metadata.
        """
        response = self._client.get(f"/domain-packs/{pack_name}")
        self._handle_response(response)
        return DomainPack(**response.json())

    # ─────────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────────────

    def _prepare_multipart(
        self,
        file: str | Path | bytes | BinaryIO,
        filename: str | None,
        domain_pack: str | None,
        include_confidence: bool,
        include_bounding_boxes: bool,
        language: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Prepare multipart form data for upload."""
        files: dict[str, Any] = {}
        data: dict[str, Any] = {}

        # Handle file input
        if isinstance(file, (str, Path)):
            path = Path(file)
            files["file"] = (path.name, open(path, "rb"), "application/octet-stream")
        elif isinstance(file, bytes):
            if not filename:
                raise ValidationError("filename is required when file is bytes")
            files["file"] = (filename, file, "application/octet-stream")
        else:
            # File-like object
            fname = filename or getattr(file, "name", "document")
            files["file"] = (fname, file, "application/octet-stream")

        if domain_pack:
            data["domain_pack"] = domain_pack

        # Options as JSON
        import json

        options = {
            "include_confidence": include_confidence,
            "include_bounding_boxes": include_bounding_boxes,
            "language": language,
        }
        data["options"] = json.dumps(options)

        return files, data

    def _handle_response(self, response: httpx.Response) -> None:
        """Handle HTTP response and raise appropriate errors."""
        if response.is_success:
            return

        try:
            error_data = response.json()
            message = error_data.get("message", response.reason_phrase)
            code = error_data.get("code", f"http_{response.status_code}")
        except Exception:
            message = response.reason_phrase or "Unknown error"
            code = f"http_{response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(message)
        elif response.status_code == 429:
            raise RateLimitError(message)
        elif response.status_code in (400, 422):
            raise ValidationError(message)
        else:
            raise AutofillerError(message, code)

    def _parse_extract_result(self, data: dict[str, Any]) -> ExtractResult:
        """Parse API response into ExtractResult."""
        return ExtractResult(
            id=data["id"],
            status=data["status"],
            domain_pack=data["domain_pack"],
            data=data["data"],
            confidence=data.get("confidence"),
            bounding_boxes=data.get("bounding_boxes"),
            metadata=ExtractionMetadata(**data.get("metadata", {})),
            warnings=data.get("warnings"),
        )


class AsyncAutofillerClient:
    """
    Asynchronous client for the Autofiller API.

    Example:
        >>> async with AsyncAutofillerClient(api_key="your-api-key") as client:
        ...     result = await client.extract(file="./invoice.pdf")
        ...     print(result.data)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the async client."""
        if not api_key:
            raise ValidationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def __aenter__(self) -> "AsyncAutofillerClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def health(self) -> HealthStatus:
        """Check API health status."""
        response = await self._client.get("/health")
        self._handle_response(response)
        return HealthStatus(**response.json())

    async def extract(
        self,
        file: str | Path | bytes | BinaryIO,
        *,
        filename: str | None = None,
        domain_pack: str | None = None,
        include_confidence: bool = True,
        include_bounding_boxes: bool = False,
        language: str = "en",
    ) -> ExtractResult:
        """Extract data from a document."""
        files, data = self._prepare_multipart(
            file=file,
            filename=filename,
            domain_pack=domain_pack,
            include_confidence=include_confidence,
            include_bounding_boxes=include_bounding_boxes,
            language=language,
        )

        response = await self._client.post("/extract", files=files, data=data)
        self._handle_response(response)
        return self._parse_extract_result(response.json())

    async def extract_async(
        self,
        file: str | Path | bytes | BinaryIO,
        *,
        filename: str | None = None,
        domain_pack: str | None = None,
        webhook_url: str | None = None,
        include_confidence: bool = True,
        include_bounding_boxes: bool = False,
        language: str = "en",
    ) -> dict[str, Any]:
        """Start an async extraction job."""
        files, data = self._prepare_multipart(
            file=file,
            filename=filename,
            domain_pack=domain_pack,
            include_confidence=include_confidence,
            include_bounding_boxes=include_bounding_boxes,
            language=language,
        )

        if webhook_url:
            data["webhook_url"] = webhook_url

        response = await self._client.post("/extract/async", files=files, data=data)
        self._handle_response(response)
        return response.json()

    async def get_job(self, job_id: str) -> JobStatus:
        """Get job status."""
        response = await self._client.get(f"/jobs/{job_id}")
        self._handle_response(response)
        data = response.json()

        if data.get("result"):
            data["result"] = self._parse_extract_result(data["result"])

        return JobStatus(**data)

    async def wait_for_job(
        self,
        job_id: str,
        *,
        poll_interval: float = 2.0,
        max_wait: float = 300.0,
    ) -> ExtractResult:
        """Wait for job completion with polling."""
        import asyncio

        start_time = time.time()

        while time.time() - start_time < max_wait:
            job = await self.get_job(job_id)

            if job.status == "completed" and job.result:
                return job.result

            if job.status == "failed":
                error_msg = job.error.get("message", "Job failed") if job.error else "Job failed"
                raise ExtractionError(error_msg)

            await asyncio.sleep(poll_interval)

        raise AutofillerError("Job timed out", "job_timeout")

    async def list_domain_packs(self) -> list[DomainPack]:
        """List available domain packs."""
        response = await self._client.get("/domain-packs")
        self._handle_response(response)
        return [DomainPack(**pack) for pack in response.json().get("items", [])]

    async def get_domain_pack(self, pack_name: str) -> DomainPack:
        """Get domain pack details."""
        response = await self._client.get(f"/domain-packs/{pack_name}")
        self._handle_response(response)
        return DomainPack(**response.json())

    # Reuse sync client helpers
    _prepare_multipart = AutofillerClient._prepare_multipart
    _handle_response = AutofillerClient._handle_response
    _parse_extract_result = AutofillerClient._parse_extract_result
