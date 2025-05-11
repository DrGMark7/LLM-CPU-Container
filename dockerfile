FROM python:3.12-bookworm

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN which pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN python -m pip install intel-extension-for-pytorch
RUN python -m pip install oneccl_bind_pt --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/cpu/cn/
RUN pip install accelerate
RUN pip install transformers==4.48.0

# Copy the application code
COPY worker_service/ ./worker_service/
COPY cmd/ ./cmd/
COPY proto/ ./proto/
COPY llm/ ./llm/

# Set the entrypoint
CMD ["python", "cmd/main.py"]
