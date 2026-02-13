# LocalAGI (LocalAI)

LocalAGI is a self-hosted AI runtime provided by **LocalAI** that enables you to run large language models (LLMs), embeddings, speech, vision, and tool-calling locally on your own infrastructure. It exposes an OpenAI-compatible API and is designed to run efficiently on CPUs and GPUs using containerised deployments.

This document describes how to **clone the LocalAI repository locally** and **run LocalAGI using Docker**.

---

## Prerequisites

### Required
- Linux, macOS, or Windows
- Git
- Docker 24+
- Docker Compose v2

### Optional (GPU support)
- NVIDIA GPU
- CUDA 11.8+ or 12.x
- NVIDIA Container Toolkit

Verify GPU support:
```bash
docker run --rm --gpus all nvidia/cuda:12.3.0-base nvidia-smi
```

---

## Clone the Repository

Clone the official LocalAI repository:

```bash
git clone https://github.com/go-skynet/LocalAI.git
cd LocalAI
```

The repository contains:
- Dockerfiles for multiple backends
- Example docker-compose configurations
- Model configuration templates
- Documentation and scripts

---

## Directory Layout (Recommended)

Create a directory for models outside the container:

```bash
mkdir -p models
```

This directory will be mounted into the container so models persist across restarts.

---

## Running LocalAGI with Docker Compose

### CPU-only Deployment

From the root of the cloned repository:

```bash
docker compose up -d
```

By default, this will:
- Build or pull the LocalAI image
- Start the LocalAGI API server
- Expose the API on port 8080

---

### GPU Deployment (NVIDIA)

Ensure the NVIDIA Container Toolkit is installed, then run:

```bash
docker compose up -d
```

If your environment requires explicit GPU configuration, confirm that the compose file includes:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - capabilities: [gpu]
```

---

## Accessing the API

Once running, LocalAGI will be available at:

```
http://localhost:8080
```

Health check:

```bash
curl http://localhost:8080/health
```

---

## Installing Models

Models are stored in the mounted models directory and configured via YAML files.

### Example: GGUF Model

```bash
mkdir -p models/llama3
```

Download a model file into that directory, then create a configuration file:

```yaml
# models/llama3/model.yaml
name: llama3
backend: llama-cpp
model: model.gguf
context_size: 8192
threads: 8
gpu_layers: 40
```

Restart the container to load the model:

```bash
docker compose restart
```

---

## Testing a Chat Completion

LocalAGI exposes an OpenAI-compatible API.

```bash
curl http://localhost:8080/v1/chat/completions   -H "Content-Type: application/json"   -d '{
    "model": "llama3",
    "messages": [
      {"role": "user", "content": "Hello from LocalAGI"}
    ]
  }'
```

---

## Configuration Notes

Common environment variables:

| Variable | Description |
|--------|-------------|
| MODELS_PATH | Path to mounted models directory |
| DEBUG | Enable verbose logging |
| THREADS | CPU threads |
| CONTEXT_SIZE | Default context size |
| CUDA_VISIBLE_DEVICES | Select GPUs |

Model-specific settings should be placed in each model’s YAML configuration.

---

## Logs and Troubleshooting

View logs:

```bash
docker logs localai
```

Common issues:
- Models not appearing: check model YAML and restart
- Out-of-memory errors: reduce context size or GPU layers
- Slow inference: adjust threads or use GPU acceleration

---

## Updating the Repository

Pull the latest changes and rebuild:

```bash
git pull
docker compose down
docker compose up -d --build
```

---

## Documentation and Resources

- https://localai.io
- https://localai.io/docs
- https://github.com/go-skynet/LocalAI

---

## License

LocalAI / LocalAGI is released under the MIT License.
Individual models may be distributed under separate licenses.
