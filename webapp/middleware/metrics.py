import os
from time import monotonic
from typing import Any, Awaitable, Callable, Dict, List

import prometheus_client
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, generate_latest
from prometheus_client.multiprocess import MultiProcessCollector
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

DEFAULT_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.125,
    0.15,
    0.175,
    0.2,
    0.25,
    0.3,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    float('+inf'),
)

# histogram_quantile(0.99, sum(rate(sirius_deps_latency_seconds_bucket[1m])) by (le, endpoint))
# среднее время обработки за 1 мин

REQUESTS_COUNT = prometheus_client.Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint"],
)

COUNT_2XX_STATUS_CODES = prometheus_client.Counter(
    "http_2xx_total",
    "Total number of HTTP 2xx response status codes",
    ["method", "endpoint"],
)

COUNT_4XX_STATUS_CODES = prometheus_client.Counter(
    "http_4xx_total",
    "Total number of HTTP 4xx response status codes",
    ["method", "endpoint"],
)

COUNT_5XX_STATUS_CODES = prometheus_client.Counter(
    "http_5xx_total",
    "Total number of HTTP 5xx response status codes",
    ["method", "endpoint"],
)

REQUESTS_LATENCY = prometheus_client.Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=DEFAULT_BUCKETS,
)

INTEGRATIONS_LATENCY = prometheus_client.Histogram(
    "integrations_latency_seconds",
    "Integration request latency",
    ['integration'],
    buckets=DEFAULT_BUCKETS,
)


# A middleware to count Prometheus metrics
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = monotonic()
        response = await call_next(request)
        process_time = monotonic() - start_time

        REQUESTS_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
        REQUESTS_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)

        if 200 <= response.status_code < 300:
            COUNT_2XX_STATUS_CODES.labels(method=request.method, endpoint=request.url.path).inc()
        elif 400 <= response.status_code < 500:
            COUNT_4XX_STATUS_CODES.labels(method=request.method, endpoint=request.url.path).inc()
        elif 500 <= response.status_code < 600:
            COUNT_5XX_STATUS_CODES.labels(method=request.method, endpoint=request.url.path).inc()

        return response


def integration_latency(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    async def wrapper(*args: List[Any], **kwargs: Dict[Any, Any]) -> Awaitable[Any]:
        start_time: float = monotonic()
        result = await func(*args, **kwargs)
        INTEGRATIONS_LATENCY.labels(integration=func.__name__).observe(monotonic() - start_time)
        return result

    return wrapper


def metrics(request: Request) -> Response:
    if 'prometheus_multiproc_dir' in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    return Response(generate_latest(registry), headers={'Content-Type': CONTENT_TYPE_LATEST})
