FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY configs ./configs
COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "mars_ml_pipeline.services.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
