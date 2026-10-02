
import logging
import time

from fastapi import FastAPI, Request

from backend.api.routes.health import router as health_router
from backend.core.config import settings
from backend.core.logging_config import configure_logging

configure_logging(settings.debug)
logger = logging.getLogger("cybermind.api")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Domain-specialized cybersecurity AI system",
    debug=settings.debug,
)

app.include_router(health_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - start_time
        logger.exception(
            "%s %s failed after %.3f seconds",
            request.method,
            request.url.path,
            duration,
        )
        raise

    duration = time.perf_counter() - start_time
    logger.info(
        "%s %s -> %s (%.3f seconds)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


@app.get("/", tags=["General"])
def root():
    return {
        "name": settings.app_name,
        "status": "online",
        "version": settings.app_version,
    }
