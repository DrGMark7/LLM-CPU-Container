# LLM-CPU-Container
LLM Inference Container Optimization for Intel CPU only

# gRPC Worker Client

A Python client for polling and processing jobs from a gRPC job queue server.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GRPC_SERVER` | gRPC server address (host:port) | `localhost:50051` |
| `POLLING_INTERVAL_MS` | Interval between job polls in milliseconds | `5000` (5 seconds) |

## Usage

Run the worker client using the provided script:
```
python cmd/main.py
```

Run the worker client using container:
```
docker build -t llm-cpu-container .
docker run --network host llm-cpu-container:latest
```

