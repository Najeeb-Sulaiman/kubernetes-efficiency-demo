
import hashlib
import os
import time

from fastapi import FastAPI, Query

app = FastAPI(title="Customer Event Processor")

INSTANCE_ID = os.getenv("HOSTNAME", "local")


@app.get("/")
def home():
    return {
        "service": "customer-event-processor",
        "instance": INSTANCE_ID,
        "message": "Ready to process customer events"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/process")
def process_events(
    duration: float = Query(default=1.0, ge=0.1, le=10.0)
):
    """
    Simulate CPU-intensive customer event processing.

    The duration parameter controls approximately how long
    the application spends performing computation.
    """
    start_time = time.time()
    data = b"customer-event-payload"

    iterations = 0

    while time.time() - start_time < duration:
        data = hashlib.sha256(data).digest()
        iterations += 1

    return {
        "instance": INSTANCE_ID,
        "processing_time_seconds": round(time.time() - start_time, 2),
        "iterations": iterations,
        "status": "processed"
    }
