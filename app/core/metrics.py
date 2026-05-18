import time

from fastapi import Request
from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware


HTTP_REQUESTS_TOTAL = Counter(
    "fastapi_http_requests_total",
    "Total HTTP requests handled by FastAPI.",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "fastapi_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path"],
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "fastapi_http_requests_in_progress",
    "HTTP requests currently being processed.",
    ["method", "path"],
)

USERS_TOTAL = Gauge(
    "app_users_total",
    "Current number of users in the application database.",
)

USERS_CREATED_TOTAL = Counter(
    "app_users_created_total",
    "Total number of users created through the application.",
)

USERS_DELETED_TOTAL = Counter(
    "app_users_deleted_total",
    "Total number of users deleted through the application.",
)

ORDERS_TOTAL_PURCHASE_PRICE = Gauge(
    "app_orders_total_purchase_price",
    "Total price of all purchases stored in the orders table.",
)


def _request_path(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path

        if path == "/metrics":
            return await call_next(request)

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, path=path).inc()
        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            observed_path = _request_path(request)
            duration = time.perf_counter() - start_time
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, path=path).dec()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                path=observed_path,
            ).observe(duration)
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=observed_path,
                status_code=str(status_code),
            ).inc()
