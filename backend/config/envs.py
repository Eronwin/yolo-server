import os

# Database configuration
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))

# Proxy configuration
PROXY_TIMEOUT = int(os.getenv("PROXY_TIMEOUT_SECONDS", 1800))

# HTTP client TCP connector configuration
TCP_CONNECTOR_LIMIT = int(os.getenv("TCP_CONNECTOR_LIMIT", 1000))
