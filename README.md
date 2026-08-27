# SircuitLab Home Server

SircuitLab is a personal home-server and electronics lab built on Ubuntu and Docker.

The server is being developed as a central platform for system monitoring, web applications, databases, automation, electronics projects, and future local-AI workloads.

**Project name:** SircuitLab

---

## Hardware

| Component | Details |
|---|---|
| Manufacturer | HP |
| Model | HP Pavilion x360 Convertible 14-dy0xxx |
| CPU | Intel Core i3-1125G4 |
| RAM | 8 GB |
| Storage | NVMe SSD |
| Network | Wi-Fi |

---

## Software Stack

- Ubuntu Linux
- Docker
- Docker Compose
- Nginx
- Python
- FastAPI
- Uvicorn
- psutil
- PostgreSQL 16
- Git

---

## Project Structure

```text
sircuitlab-home-server/
|
+-- apps/
|   |
|   +-- api/
|   |   +-- main.py
|   |   +-- requirements.txt
|   |
|   +-- dashboard/
|       +-- Dockerfile
|       +-- index.html
|       +-- system.html
|       +-- nginx.conf
|
+-- config/
+-- data/
+-- docker/
+-- docs/
+-- hardware/
+-- scripts/
|
+-- README.md