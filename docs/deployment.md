# Deployment

This document explains how to run **all backend components** of Intilaq AI using **Docker Compose**, as well as the purpose of each Dockerfile and reverse proxy config used in deployment.

---

## 1. Stack Overview

The application is deployed using Docker Compose and includes the following services:

- MongoDB (NoSQL)
- PostgreSQL (Relational)
- Redis (In-memory store for tokens)
- FastAPI backend
- Whisper-based STT microservice
- RQ worker for background jobs
- NGINX for reverse proxy + HTTPS termination

---

## 2. Docker Compose File

Defined in `docker-compose.yml`.

### Services

- `mongodb`: Stores sessions, answers, and interview content.
- `redis`: Stores temporary access/refresh tokens.
- `postgres`: Stores structured data like HR users, normal users.
- `speech_to_text_service`: Whisper-powered FastAPI app.
- `fastapi`: Main backend running on port 8000.
- `rq_worker`: Background worker for processing video/audio jobs.
- `nginx`: Reverse proxy, forwards requests to `fastapi`, serves over HTTPS.

## 3. Tailscale Integration

### What is Tailscale?

Tailscale is a secure VPN mesh network that allows different services or devices to communicate **privately** over an encrypted tunnel, **without exposing ports** to the public internet.

---

### Tailscale 

In the Intilaq AI deployment:

- Tailscale is used to **securely connect the backend (FastAPI)** to the **frontend**, especially during development.
- The backend is **accessible via a static Tailscale HTTPS domain**, such as:











