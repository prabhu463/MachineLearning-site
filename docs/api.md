# API Documentation

Base URL: `/api/v1`

## Health

`GET /health`

Returns service health.

## Metrics

`POST /metrics`

Stores a metric payload.

`GET /metrics?limit=50`

Lists recent metrics.

## Predictions

`POST /predict?auto_execute=true`

Runs inference, stores incidents when risk is high, and simulates remediation.

## Incidents

`GET /incidents?limit=50`

Lists incidents.

`PATCH /incidents/{incident_id}`

Updates incident status and notes.

## Actions

`GET /actions?limit=50`

Lists remediation actions.

## Dashboard

`GET /dashboard/summary`

Returns aggregate stats for the dashboard.
