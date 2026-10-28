"""WeatherGPT: AI-Powered Multilingual Weather Forecasting and Alert Assistant
Shared Python FastAPI Backend Service
SIH Problem Statement ID: SIH26068
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api.v1.router import api_router
from backend.app.config import settings
from backend.app.schemas.common import APIResponse
from backend.app.utils.exceptions import WeatherGPTException
from backend.app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION} [{settings.APP_ENV}]")
    logger.info(f"Primary Meteorological Provider: {settings.PRIMARY_WEATHER_PROVIDER}")
    logger.info(f"AI Assistant Provider: {settings.AI_PROVIDER}")
    logger.info(f"Supported Languages: {', '.join(settings.SUPPORTED_LANGUAGES)}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "Shared high-performance backend serving the WeatherGPT responsive web application "
        "and native Android mobile application. Delivers verified real-time weather observations, "
        "hourly and multi-day forecasts, severe weather alerts, and context-grounded multilingual "
        "conversational AI assistance in English, Hindi, and Marathi."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(WeatherGPTException)
async def weathergpt_exception_handler(request: Request, exc: WeatherGPTException):
    logger.warning(f"Domain Exception on {request.url.path}: {exc.message} (status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            message=exc.message,
            error=str(exc.detail) if exc.detail else exc.message,
            data=None,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = "; ".join([f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors])
    logger.warning(f"Validation error on {request.url.path}: {error_msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=APIResponse(
            success=False,
            message="Request validation failed. Please check query or body parameters.",
            error=error_msg,
            data=None,
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            message=str(exc.detail),
            error=str(exc.detail),
            data=None,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            message="An internal server error occurred.",
            error=str(exc) if settings.DEBUG else "Internal Server Error",
            data=None,
        ).model_dump(),
    )


# Attach v1 API Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "health": "/api/v1/health",
    }
