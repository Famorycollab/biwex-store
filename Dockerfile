ARG PYTHON_VERSION=3.11

# Étape 1 : installation des dépendances dans un environnement virtuel
FROM python:${PYTHON_VERSION}-slim AS builder
WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 180 -r requirements.txt
# Étape 2 : image finale légère
FROM python:${PYTHON_VERSION}-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . .
RUN useradd -m appuser && mkdir -p /app/instance && chown -R appuser /app
USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
