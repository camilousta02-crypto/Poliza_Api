# ---- Etapa 1: instala dependencias ----
FROM python:3.11.9-slim-bookworm AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Etapa 2: imagen final ----
FROM python:3.11.9-slim-bookworm
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# Valores de ejemplo para que arranque sin .env; en un despliegue real se sobreescriben con -e o --env-file
ENV DATABASE_URL=sqlite:////app/data/app.db \
    SECRETO_FIRMA=cambia-este-valor-al-desplegar \
    CLAVE_API_REASEGURO=cambia-este-valor-al-desplegar

USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status == 200 else 1)"
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
