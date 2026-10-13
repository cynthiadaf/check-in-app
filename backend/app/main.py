"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.dashboard import router as dashboard_router
from app.api.guest_entries import router as guest_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(guest_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """Return all application HTTP errors in the documented shape."""
    if isinstance(exc.detail, dict) and "detail" in exc.detail and "code" in exc.detail:
        content = exc.detail
    else:
        content = {"detail": str(exc.detail), "code": "HTTP_ERROR"}
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Return validation errors with a stable code and human-readable details."""
    errors = [
        {"loc": list(error.get("loc", ())), "msg": error.get("msg", "Invalid value"), "type": error.get("type", "value_error")}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed", "code": "VALIDATION_ERROR", "errors": errors},
    )


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Return a lightweight liveness response."""
    return {"status": "ok"}
