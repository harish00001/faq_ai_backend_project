from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.database import Base, engine
from app.models.faq import FAQ  # noqa: F401
from app.services.index_service import index_service

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_application", extra={"env": settings.app_env})
    Base.metadata.create_all(bind=engine)
    index_service.initialize()
    yield
    logger.info("stopping_application")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


app.include_router(api_router, prefix=settings.api_v1_str)
