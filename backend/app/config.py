# NOTE: This is a legacy stub kept for reference only.
# The active configuration lives in backend/app/core/config.py (pydantic-settings).

# Security Configurations
SECRET_KEY = "prod-secret-key-generated-from-environment-variables"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TTL = 86400  # 24 hours

# Rate Limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 10,
    "prefix": "rl:",
    "storage": "redis",
}

# Redis Config
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# OpenTelemetry Configuration
OTEL_SERVICE_NAME = "backend-service"
OTEL_EXPORTER_OTLP_ENDPOINT = "http://otel-collector:4317"