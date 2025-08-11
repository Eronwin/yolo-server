# ------------------------------------------------------------
# Build process:
# 1) builder stage:
#    - Use python:slim
#    - Install "build"
#    - Build wheel
# 2) runtime stage:
#    - Use python:slim
#    - apt-get install tini
#    - Install the wheel and run via tini
# Notes:
# - Keep the image minimal: only essential packages
# - CLI entrypoint is "python-server-init" (declared in pyproject.toml)
# - Mount /etc/python-server-init/config.yaml or override CMD as needed
# ------------------------------------------------------------

ARG PYTHON_VERSION=3.12

# ---------- Stage 1: builder (build wheel) ----------
FROM python:${PYTHON_VERSION}-slim AS builder
WORKDIR /build
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install only what's needed to build the wheel
RUN pip install --no-cache-dir build

# Copy project files required to build
COPY pyproject.toml README.md ./
COPY backend ./backend

# Build wheel into /build/dist and cleanup
RUN python -m build && (pip cache purge || true)

# ---------- Stage 2: runtime (apt install tini, run CLI) ----------
FROM python:${PYTHON_VERSION}-slim AS runtime
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install tini via apt and cleanup apt lists in the same layer
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini; \
    rm -rf /var/lib/apt/lists/*

# Install the built wheel and cleanup pip cache
COPY --from=builder /build/dist/python_server_init-*.whl /tmp/
RUN set -eux; \
    pip install --no-cache-dir /tmp/python_server_init-*.whl; \
    rm -f /tmp/python_server_init-*.whl; \
    (pip cache purge || true); \
    rm -rf /root/.cache/pip || true

# Optional config directory (empty by default; mount your own file)
RUN mkdir -p /etc/python-server-init && rm -rf /tmp/*

# Expose service port (adjust if needed)
EXPOSE 80

# Use tini as PID 1, then hand over to the CLI
ENTRYPOINT ["tini", "--", "python-server-init", "start"]
