# SircuitLab Home Server

SircuitLab is a personal home-server and electronics lab built on Ubuntu and Docker.

The server is being developed as a central platform for system monitoring, web applications, databases, automation, electronics projects, and future local-AI workloads.

Project name: SircuitLab

## Hardware

Manufacturer: HP
Model: HP Pavilion x360 Convertible 14-dy0xxx
CPU:  Intel i3-1125G4
RAM: 8 GB
Storage: NVMe SSD
Network: Wi-Fi

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


## Project Structure

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


## Architecture

                 Browser
                    |
                    | :8080
                    v
          +-------------------+
          | SircuitLab        |
          | Dashboard / Nginx |
          +---------+---------+
                    |
                    | API
                    v
          +-------------------+
          | SircuitLab API    |
          | FastAPI :8000     |
          +---------+---------+
                    |
                    v
               Linux Host
                Hardware

          +-------------------+
          | PostgreSQL 16     |
          | :5432             |
          +-------------------+


## Dashboard

The SircuitLab dashboard is served through Nginx.

The UI uses a black btop-inspired terminal theme with:

- Technical/monospace typography
- Compact panels
- CPU graphs
- Memory graphs
- Storage information
- Network information
- Temperature information
- Battery information
- Process monitoring
- System uptime
- Automatic updates

The system monitor refreshes automatically every 1 second.


## System Monitor

The system monitor is located at:

apps/dashboard/system.html

The backend uses psutil to collect system information.

Current monitoring includes:

- CPU usage
- CPU cores/threads
- Memory usage
- Disk usage
- Network statistics
- Temperature sensors
- Battery status
- System uptime
- Running processes


## API

The API is located at:

apps/api/main.py

It runs using FastAPI and Uvicorn.

Test the API:

curl http://localhost:8000/health

System information:

curl http://localhost:8000/api/system


## Dashboard Access

The dashboard runs on port 8080.

Test from the server:

curl -I http://localhost:8080

Expected:

HTTP/1.1 200 OK

Find the server IP:

hostname -I

Then open:

http://SERVER-IP:8080

from another device on the network.


## Docker

Check running containers:

docker ps

Check all containers:

docker ps -a

Main containers:

sircuitlab-dashboard
sircuitlab-api
sircuitlab-postgres

Check logs:

docker logs sircuitlab-dashboard --tail 50
docker logs sircuitlab-api --tail 50
docker logs sircuitlab-postgres --tail 50

Follow logs:

docker logs -f sircuitlab-dashboard


## Automatic Start After Reboot

The containers use Docker's unless-stopped restart policy.

Configure it:

docker update --restart unless-stopped \
sircuitlab-dashboard \
sircuitlab-api \
sircuitlab-postgres

Verify:

docker inspect -f '{{.Name}} -> {{.HostConfig.RestartPolicy.Name}}' \
sircuitlab-dashboard \
sircuitlab-api \
sircuitlab-postgres

Expected:

/sircuitlab-dashboard -> unless-stopped
/sircuitlab-api -> unless-stopped
/sircuitlab-postgres -> unless-stopped

After a server reboot:

docker ps

The containers should start automatically.


## Starting Containers

If the containers are stopped:

docker start sircuitlab-postgres sircuitlab-api sircuitlab-dashboard


## Restarting Containers

Restart the services:

docker restart sircuitlab-postgres sircuitlab-api sircuitlab-dashboard


## Rebuilding the Dashboard

After editing dashboard files:

cd ~/sircuitlab-home-server

Build the dashboard:

docker build -t sircuitlab-dashboard ./apps/dashboard

Restart it:

docker restart sircuitlab-dashboard

If Docker Compose is being used:

docker compose build dashboard
docker compose up -d dashboard


## Full Rebuild

If a complete rebuild is required:

cd ~/sircuitlab-home-server

docker compose down
docker compose build
docker compose up -d

Do not use this unless required:

docker compose down -v

The -v option can remove Docker volumes and may delete PostgreSQL data.


## Dashboard Troubleshooting

If the dashboard does not open:

docker ps -a

Then check:

docker logs sircuitlab-dashboard --tail 50

Test:

curl -I http://localhost:8080


## API Troubleshooting

Check API logs:

docker logs sircuitlab-api --tail 50

Test:

curl http://localhost:8000/health

Then:

curl http://localhost:8000/api/system


## Checking Dashboard Files

Check files inside the running container:

docker exec sircuitlab-dashboard ls -l /usr/share/nginx/html/

Check system.html:

docker exec sircuitlab-dashboard ls -l /usr/share/nginx/html/system.html

Test the page:

curl -I http://localhost:8080/system.html


## Docker Networking Issue

During development, the dashboard container failed to start because Nginx could not resolve:

sircuitlab-api

The error was similar to:

nginx: [emerg] host not found in upstream "sircuitlab-api"

The problem was Docker networking.

Containers need to be connected to the same Docker network when they communicate using container/service names.

Important:

localhost

inside a container refers to that container itself, not another Docker container.

Check Docker networks:

docker network ls

Inspect a network:

docker network inspect NETWORK_NAME


## Fetch Debugging

fetch() is JavaScript and cannot be executed directly in the Linux terminal.

This is incorrect in Bash:

fetch('/api/system')

Use curl from the server instead:

curl http://localhost:8000/api/system

fetch() belongs inside the dashboard JavaScript or browser developer console.


## Process Monitor

The dashboard includes process monitoring.

The process monitor receives process information from the API and should update automatically.

When debugging:

curl http://localhost:8000/api/system

If the API returns current process information but the UI does not update, check the browser console for JavaScript errors and verify that the frontend refresh logic is running.


## Temperature Monitoring

Check Linux temperature sensors:

sensors

If sensors is not installed:

sudo apt install lm-sensors

Then:

sensors

Available sensors depend on the motherboard, kernel and drivers.


## Battery Monitoring

The system exposed:

/sys/class/power_supply/

with:

ADP1
BAT0

Available charge files included:

charge_full
charge_full_design
charge_now

The system did not expose a standard charging-threshold file such as:

charge_control_end_threshold

The machine was identified as:

HP
HP Pavilion x360 Convertible 14-dy0xxx

At the time of testing, the battery status was:

Discharging

Therefore, an 80% charging limit could not be configured through the available sysfs interface that was checked.


## PostgreSQL

PostgreSQL 16 runs in its own Docker container:

sircuitlab-postgres

Database port:

5432

PostgreSQL data should be kept protected from unnecessary public network access.

Avoid deleting Docker volumes unless the database data is intentionally being removed.

## Useful Docker Commands

docker ps
docker ps -a
docker images
docker network ls
docker start CONTAINER
docker stop CONTAINER
docker restart CONTAINER
docker logs CONTAINER
docker inspect CONTAINER


## Quick SircuitLab Health Check

Run:

cd ~/sircuitlab-home-server

docker ps

curl http://localhost:8000/health

curl http://localhost:8000/api/system

curl -I http://localhost:8080

If all of these work, the main SircuitLab stack is operational.


## Current Status

Completed:

- Ubuntu server setup
- Docker setup
- PostgreSQL 16
- FastAPI backend
- Nginx dashboard
- System monitoring API
- CPU monitoring
- Memory monitoring
- Storage monitoring
- Network monitoring
- Temperature monitoring
- Battery monitoring
- Process monitoring
- System uptime
- btop-inspired dashboard
- System graphs
- Automatic 1-second dashboard refresh
- Docker automatic restart after reboot
- Git repository

Next:

- Improve process monitoring
- Add deeper disk/NVMe monitoring
- Add Docker container monitoring
- Add service status monitoring
- Add secure remote access
- Expand automation and electronics integrations
- Add local AI services


## SircuitLab

SircuitLab is being built as a personal home-server, electronics and software lab.

The priority is to keep the system reliable, modular, easy to debug, easy to rebuild, properly documented, clean and expandable.