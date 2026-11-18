"""Domain exceptions and global FastAPI exception handlers.

All error responses comply with RFC 9457 (Problem Details for HTTP APIs).
No response may use FastAPI's default {"detail": "..."} format.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.schemas import ApiError, InvalidParam

# ---------------------------------------------------------------------------
# Error type URIs (RFC 9457 §3.1)
# ---------------------------------------------------------------------------

_BASE = "https://api.character-build.dev/errors"

URI_BAD_REQUEST        = f"{_BASE}/bad-request"
URI_UNAUTHORIZED       = f"{_BASE}/unauthorized"
URI_FORBIDDEN          = f"{_BASE}/forbidden"
URI_NOT_FOUND          = f"{_BASE}/not-found"
URI_VALIDATION_ERROR   = f"{_BASE}/validation-error"
URI_INTERNAL           = f"{_BASE}/internal-server-error"

_HTTP_URI_MAP: dict[int, str] = {
    400: URI_BAD_REQUEST,
    401: URI_UNAUTHORIZED,
    403: URI_FORBIDDEN,
    404: URI_NOT_FOUND,
    422: URI_VALIDATION_ERROR,
}

_HTTP_TITLE_MAP: dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    422: "Unprocessable Entity",
    500: "Internal Server Error",
}


# ---------------------------------------------------------------------------
# Domain exception hierarchy
# ---------------------------------------------------------------------------


class DomainException(Exception):
    """Base class for all RFC 9457-compliant domain exceptions."""

    def __init__(
        self,
        status_code: int,
        type_uri: str,
        title: str,
        detail: str,
        invalid_params: list[InvalidParam] | None = None,
    ) -> None:
        self.status_code = status_code
        self.type_uri = type_uri
        self.title = title
        self.detail = detail
        self.invalid_params = invalid_params
        super().__init__(detail)


class BadRequestException(DomainException):
    """400 Bad Request."""

    def __init__(
        self,
        detail: str = "The request is malformed or contains invalid data.",
        invalid_params: list[InvalidParam] | None = None,
    ) -> None:
        super().__init__(
            status_code=400,
            type_uri=URI_BAD_REQUEST,
            title="Bad Request",
            detail=detail,
            invalid_params=invalid_params,
        )


class UnauthorizedException(DomainException):
    """401 Unauthorized — missing, invalid, or expired token."""

    def __init__(
        self,
        detail: str = "Authentication credentials are missing or invalid.",
    ) -> None:
        super().__init__(
            status_code=401,
            type_uri=URI_UNAUTHORIZED,
            title="Unauthorized",
            detail=detail,
        )


class ForbiddenException(DomainException):
    """403 Forbidden — authenticated but insufficient role."""

    def __init__(
        self,
        detail: str = "You do not have permission to perform this action.",
    ) -> None:
        super().__init__(
            status_code=403,
            type_uri=URI_FORBIDDEN,
            title="Forbidden",
            detail=detail,
        )


class NotFoundException(DomainException):
    """404 Not Found."""

    def __init__(self, detail: str = "The requested resource was not found.") -> None:
        super().__init__(
            status_code=404,
            type_uri=URI_NOT_FOUND,
            title="Not Found",
            detail=detail,
        )


class ValidationException(DomainException):
    """422 Unprocessable Entity."""

    def __init__(
        self,
        detail: str = "The request contains semantically invalid data.",
        invalid_params: list[InvalidParam] | None = None,
    ) -> None:
        super().__init__(
            status_code=422,
            type_uri=URI_VALIDATION_ERROR,
            title="Unprocessable Entity",
            detail=detail,
            invalid_params=invalid_params,
        )


# ---------------------------------------------------------------------------
# Helper: build a JSONResponse from an ApiError model
# ---------------------------------------------------------------------------


def _problem_response(
    request: Request,
    status_code: int,
    type_uri: str,
    title: str,
    detail: str,
    invalid_params: list[InvalidParam] | None = None,
) -> JSONResponse:
    error = ApiError(
        type=type_uri,
        title=title,
        status=status_code,
        detail=detail,
        instance=request.url.path,
        invalid_params=invalid_params,
    )
    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(by_alias=True, exclude_none=True),
    )


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    """Convert any DomainException into an RFC 9457 JSONResponse."""
    return _problem_response(
        request=request,
        status_code=exc.status_code,
        type_uri=exc.type_uri,
        title=exc.title,
        detail=exc.detail,
        invalid_params=exc.invalid_params,
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Map Pydantic/FastAPI validation failures to RFC 9457 (422)."""
    invalid_params: list[InvalidParam] = []
    for err in exc.errors():
        loc = err.get("loc", ())
        # skip the top-level 'body' / 'query' prefix when building the name
        field_parts = [str(p) for p in loc if p not in ("body", "query", "path")]
        name = ".".join(field_parts) if field_parts else ".".join(str(p) for p in loc)
        reason = err.get("msg", "Invalid value")
        invalid_params.append(InvalidParam(name=name, reason=reason))

    return _problem_response(
        request=request,
        status_code=422,
        type_uri=URI_VALIDATION_ERROR,
        title="Unprocessable Entity",
        detail="One or more fields failed validation.",
        invalid_params=invalid_params,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Convert standard FastAPI/Starlette HTTPExceptions to RFC 9457."""
    status_code = exc.status_code
    type_uri = _HTTP_URI_MAP.get(status_code, f"{_BASE}/http-error")
    title = _HTTP_TITLE_MAP.get(status_code, "HTTP Error")
    detail = str(exc.detail) if exc.detail else title
    return _problem_response(
        request=request,
        status_code=status_code,
        type_uri=type_uri,
        title=title,
        detail=detail,
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler — never expose internal stack traces."""
    return _problem_response(
        request=request,
        status_code=500,
        type_uri=URI_INTERNAL,
        title="Internal Server Error",
        detail="An unexpected error occurred. Please try again later.",
    )


# ---------------------------------------------------------------------------
# Registration helper (called from main.py)
# ---------------------------------------------------------------------------


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all RFC 9457 handlers to the FastAPI application."""
    app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)
