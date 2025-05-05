FROM python:3.12-bookworm

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN which pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY worker_service/ ./worker_service/
COPY cmd/ ./cmd/
COPY proto/ ./proto/
COPY llm/ ./llm/

# Set environment variables with defaults
ENV GRPC_SERVER=localhost:50051
ENV POLLING_INTERVAL_MS=5000

# Set the entrypoint
CMD ["python", "cmd/main.py"]
