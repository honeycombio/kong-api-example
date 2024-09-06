import os
import time
import requests
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": "client"})
trace.set_tracer_provider(TracerProvider(resource=resource))

COLLECTOR_HOST = os.environ.get("COLLECTOR_HOST", "otel-collector")
COLLECTOR_PORT = os.environ.get("COLLECTOR_PORT", "4318")

otlp_exporter = OTLPSpanExporter(
    endpoint=f"http://{COLLECTOR_HOST}:{COLLECTOR_PORT}/v1/traces",
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument the requests library
RequestsInstrumentor().instrument()

# Kong gateway URL
KONG_URL = os.environ.get("KONG_URL", "http://kong:8000")

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def call_service(service_name):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(f"call_{service_name}") as span:
        try:
            url = f"{KONG_URL}/{service_name}"
            span.set_attribute("http.url", url)
            span.set_attribute("http.method", "GET")
            
            with tracer.start_as_current_span("http_request") as request_span:
                response = requests_retry_session().get(url, timeout=5)
                response.raise_for_status()
            
            span.set_attribute("http.status_code", response.status_code)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error calling {service_name}: {str(e)}")
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR, str(e))
            return {"error": str(e)}

if __name__ == "__main__":
    tracer = trace.get_tracer(__name__)
    
    iteration = 0
    while True:
        with tracer.start_as_current_span(f"service_calls_iteration_{iteration}"):
            logger.info(f"Iteration {iteration}")
            logger.info("Calling Service 1:")
            result1 = call_service("service1")
            logger.info(result1)
            
            logger.info("Calling Service 2:")
            result2 = call_service("service2")
            logger.info(result2)
            
        logger.info("Waiting for 5 seconds...\n")
        time.sleep(5)
        
        iteration += 1