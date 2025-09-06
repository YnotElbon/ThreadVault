FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only bridge code
COPY tools/bridges /app/tools/bridges
COPY system/bin /app/system/bin

COPY tools/bridges/requirements.txt /app/tools/bridges/
RUN pip install --no-cache-dir -r tools/bridges/requirements.txt

# Minimal unprivileged user
RUN useradd -m appuser
USER appuser

ENV THREADVAULT_BASE=/vault \
    HOST=0.0.0.0 \
    PORT=8787 \
    GIT_AUTO_COMMIT=true \
    GIT_REMOTE=origin \
    GIT_BRANCH=main

VOLUME ["/vault"]

EXPOSE 8787

ENTRYPOINT ["bash", "/app/system/bin/start_bridge.sh"]

