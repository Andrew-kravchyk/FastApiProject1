# Lab 7 Monitoring

This project exposes FastAPI metrics at `/metrics` and starts a monitoring stack with Docker Compose.

## Services

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (`admin` / `admin`)
- FastAPI metrics: http://localhost:8000/metrics
- PostgreSQL exporter: http://localhost:9187/metrics
- cAdvisor container metrics: http://localhost:8081/metrics

## Dashboards

Grafana is provisioned automatically with:

- `FastAPI Application Metrics`
- `PostgreSQL and Docker Metrics`

Useful popular Grafana dashboards for manual import:

- PostgreSQL Database by prometheus exporter: `9628`
- Docker and system monitoring with cAdvisor: `14282`
- Node Exporter Full: `1860`

## Custom Metrics

- `app_users_total`
- `app_users_created_total`
- `app_users_deleted_total`
- `app_orders_total_purchase_price`
