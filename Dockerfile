FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

RUN pip install -r requirements.txt


# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with Gunicorn + Uvicorn workers
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
