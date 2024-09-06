import uvicorn
import os
import time
import requests
import logging
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": "service 1"})
trace.set_tracer_provider(TracerProvider(resource=resource))

COLLECTOR_HOST = os.environ.get("COLLECTOR_HOST", "otel-collector")
COLLECTOR_PORT = os.environ.get("COLLECTOR_PORT", "4318")

otlp_exporter = OTLPSpanExporter(
    endpoint=f"http://{COLLECTOR_HOST}:{COLLECTOR_PORT}/v1/traces"
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument the requests library
RequestsInstrumentor().instrument()

FastAPIInstrumentor.instrument_app(app)

@app.get("/")
async def root():
    return {"message": "Hello from Service 1"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)