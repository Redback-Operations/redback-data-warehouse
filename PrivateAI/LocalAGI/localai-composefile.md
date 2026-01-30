# docker-compose.local.yaml — Local customisations

This document describes the *site‑local* overrides applied to the LocalAI stack via `docker-compose.local.yaml`.
It is intended to be checked into GitHub alongside the Compose files.

The main goals of this file are:

- Proxy awareness for restricted networks (e.g. Deakin)
- Strict internal‑only networking for core services
- A single, controlled public entrypoint via Nginx
- Clear wiring between LocalAI (LLM), LocalRecall (RAG), and LocalAGI (UI)

---

## Services

### `localai` — LocalAI runtime (GPU + proxy + internal‑only)

**Purpose:**  
Runs the LocalAI server (OpenAI‑compatible API) with NVIDIA CUDA 12 GPU support.  
It is accessible *only* to other containers on the internal network.

**Key configuration:**

- **Image**
  - `localai/localai:master-gpu-nvidia-cuda-12`
  - GPU‑enabled LocalAI image built for CUDA 12.

- **Core behaviour**
  - `LOCALAI_SINGLE_ACTIVE_BACKEND=true`  
    Ensures only one backend is active at a time.
  - `DEBUG=true`  
    Enables verbose logging.

- **API key handling (optional)**
  - `LOCALAI_API_KEY` *(commented)*  
    Enables API key protection.
  - `LOCALAI_DISABLE_API_KEY_REQUIREMENT_FOR_HTTP_GET` *(commented)*  
    Allows unauthenticated GET endpoints while still protecting API calls.

- **Proxy configuration**
  - `HTTP_PROXY`, `HTTPS_PROXY`  
    Required for outbound downloads (models, galleries).
  - `NO_PROXY`  
    Prevents internal Docker traffic from going via the proxy.

- **GPU access**
  - `gpus: all`  
    Non‑swarm GPU hint to allow access to all NVIDIA GPUs.

- **Networking**
  - No published ports (`ports: []`).
  - `expose: 8080` for internal container access.
  - Attached only to the `internal` network.

- **Host resolution**
  - `extra_hosts` maps the Deakin proxy hostname to a fixed IP.

- **Healthcheck**
  - Calls `/v1/models` using the API key.
  - Confirms LocalAI is responding correctly before marking healthy.

---

### `dind` — Docker‑in‑Docker helper (proxy + internal‑only)

**Purpose:**  
Helper container that requires proxy access, typically used for build or Docker tooling tasks.

**Key configuration:**

- Proxy variables (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`)
- No exposed ports
- Attached only to the `internal` network

---

### `localrecall` — LocalRecall RAG service (proxy + internal‑only)

**Purpose:**  
Provides document ingestion and retrieval (RAG), using LocalAI as its embedding/LLM backend.

**Key configuration:**

- **Storage and RAG behaviour**
  - `COLLECTION_DB_PATH=/db`
  - `FILE_ASSETS=/assets`
  - `LOCALRECALL_CHUNK_SIZE=256`
  - `LOCALRECALL_CHUNK_OVERLAP=20`

- **Embedding model**
  - `EMBEDDING_MODEL=granite-embedding-107m-multilingual`

- **LocalAI integration**
  - `OPENAI_API_KEY=${LOCALAI_API_KEY}`
  - `OPENAI_BASE_URL=http://localai:8080`

- **Proxy configuration**
  - Outbound proxy enabled
  - Internal traffic excluded via `NO_PROXY`

- **Networking**
  - No published ports
  - `expose: 8080`
  - Attached only to the `internal` network

- **Host resolution**
  - Deakin proxy hostname mapped via `extra_hosts`

---

### `localrecall-healthcheck` — Internal healthcheck helper

**Purpose:**  
Runs health checks against LocalRecall without requiring outbound proxy access.

**Key configuration:**

- Only `NO_PROXY` is set
- No exposed ports
- Internal network only

---

### `localagi` — LocalAGI Web UI (proxy‑aware build)

**Purpose:**  
Builds and runs the LocalAGI web UI, connecting it to LocalAI for LLM calls and LocalRecall for RAG.

**Key configuration:**

- **Build‑time proxy**
  - Proxy variables passed as build args so dependencies can be fetched during image build.

- **Runtime integration**
  - `LOCALAGI_LLM_API_URL=http://localai:8080`
  - `LOCALAGI_LLM_API_KEY=${LOCALAI_API_KEY}`
  - `LOCALAGI_LOCALRAG_URL=http://localrecall:8080/api`  
    *(The `/api` path is required.)*

- **Networking**
  - No published ports
  - `expose: 3000`
  - Internal network only

---

### `nginx` — Public entrypoint and reverse proxy

**Purpose:**  
Acts as the **only** public‑facing service.  
Routes external traffic to LocalAI, LocalAGI, and LocalRecall while enforcing access controls.

**Key configuration:**

- **Dependencies**
  - Starts after `localai`, `localagi`, and `localrecall`.

- **Published ports**
  - `9081` — HTTP
  - `9443` — HTTPS
  - `9000` — Optional dedicated LocalAGI UI
  - `9080` — Optional dedicated LocalRecall endpoint

- **Security**
  - Receives `LOCALAI_API_KEY` for protecting `/v1` API routes.
  - Optional Basic Auth via `.htpasswd`.

- **Configuration**
  - Nginx site configs mounted from `./nginx/conf.d`
  - Optional TLS certificates supported.

- **Networking**
  - Connected to both `internal` and `public` networks.

---

### `sshbox` — Utility container (SSH + tools)

**Purpose:**  
A general‑purpose Ubuntu container for debugging, testing, and maintenance.

**Key configuration:**

- Proxy‑aware at build and runtime
- Internal network only
- Optional SSH port exposure if needed

---

## Networks

### `internal`
Private bridge network used for all service‑to‑service communication.
Most containers attach **only** to this network.

### `public`
Bridge network used by Nginx to expose selected services to the host.

---

## Summary

This Compose override ensures:

- Core services remain internal and isolated
- Proxy requirements are handled consistently
- All LLM and RAG traffic flows over Docker DNS
- Nginx is the single, auditable boundary to the outside world
