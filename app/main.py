import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1 import auth, pastes
from app.core.limiter import limiter
from app.core.redis_client import redis_client

# Metrics
request_count = Counter(
    "fastapi_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
request_duration = Histogram(
    "fastapi_request_duration_seconds", "HTTP request duration in seconds", ["method", "endpoint"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    await redis_client.connect()
    yield
    await redis_client.disconnect()


app = FastAPI(
    title="Pastebin Clone",
    version="1.0.0",
    description="Production-grade pastebin with FastAPI",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Trust proxy headers FIRST (IMPORTANT for NGINX)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Metrics middleware
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    """Add metrics for Prometheus"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    request_count.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    request_duration.labels(method=request.method, endpoint=request.url.path).observe(process_time)

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(pastes.router, prefix="/api/v1")


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Pastebin API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
