import asyncio
import traceback
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

load_dotenv()

from .analyzer import analyze_ticket  # noqa: E402 — after load_dotenv
from .models import TicketRequest  # noqa: E402
from .rate_limiter import limiter, MAX_REQUESTS_PER_WINDOW, WINDOW_SECONDS  # noqa: E402


async def _periodic_cleanup():
    while True:
        await asyncio.sleep(300)  # every 5 minutes
        limiter._cleanup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_periodic_cleanup())
    print(
        f"[startup] QueueStorm Investigator is ready. "
        f"Rate limit: {MAX_REQUESTS_PER_WINDOW} req/{WINDOW_SECONDS}s per IP."
    )
    yield
    task.cancel()


app = FastAPI(
    title="QueueStorm Investigator",
    description="AI/API support copilot for fintech complaint triage.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze-ticket")
async def analyze_ticket_endpoint(request: Request):
    # --- rate limiting ---
    client_ip = request.client.host if request.client else "unknown"
    allowed, retry_after = limiter.is_allowed(client_ip)
    if not allowed:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            content={
                "error": "Rate limit exceeded",
                "detail": f"Max {MAX_REQUESTS_PER_WINDOW} requests per {WINDOW_SECONDS}s. "
                          f"Retry after {retry_after}s.",
            },
        )

    # --- parse raw body (graceful 400 on bad JSON) ---
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON in request body"},
        )

    if not isinstance(body, dict):
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must be a JSON object"},
        )

    # --- schema validation ---
    try:
        ticket = TicketRequest(**body)
    except ValidationError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": "Request validation failed", "details": exc.errors()},
        )

    # --- semantic validation ---
    if not ticket.complaint or not ticket.complaint.strip():
        return JSONResponse(
            status_code=422,
            content={"error": "complaint field must not be empty"},
        )

    # --- analysis ---
    try:
        result = await analyze_ticket(ticket)
        return JSONResponse(status_code=200, content=result)
    except Exception:
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error. Please try again."},
        )
