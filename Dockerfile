FROM python:3.10.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10.12-slim

WORKDIR /app

# Copy only the compiled Python packages from the builder stage
COPY --from=builder /root/.local /root/.local

# Ensure the local binaries are on the PATH
ENV PATH=/root/.local/bin:$PATH

# Copy the Task 1 Agent code, prompt, and Data directory
COPY data/ ./data/
COPY task1/prompt.txt ./task1/
# Note: For production, we export my notebook to a Python script:
COPY task1/solution.py ./task1/

# Run the agent application
CMD ["python", "task1/solution.py"]