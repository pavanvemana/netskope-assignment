# Netskope Customer support

An async-ready microservice built using **FastAPI** for handling ticketing workflows, SLA tracking, escalation management

---

## Features

- Ticket management with status history
- SLA clock management and pause/resume tracking
- Escalation level management
- AI integration for ticket triage suggestions (LLM + RAG) (Pending)
- Prometheus-compatible metrics for observability (Pending)
- Asynchronous, production-ready FastAPI app

---

## 📦 Tech Stack

- **FastAPI**
- **SQLAlchemy + PostgreSQL**
- **Docker**
- **asyncio**
- **Swagger**
- **Celery**
- **Redis**

---

## 🛠️ Local Setup

### 📑 Requirements
- Docker

### 📦 Running the app

- Change directory to cs-app
- Build images for Application and DB
    ```
    docker compose build app
    docker compose build db
    ```
- Get the app up and running
    ```
    docker compose up -d (Runs in background)
    ```
- Access the app at `http://localhost:8000` using Postman or other tools (No UI available)
- For API docs please go to `http://localhost:8000/docs`


