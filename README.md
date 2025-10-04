# Network Device Status Monitoring System

A full-stack network device monitoring application. This system demonstrates containerization, caching strategies, database integration, and real-time monitoring capabilities.

## Project Overview

This application monitors network devices and displays their status through a web dashboard. It simulates real-time device monitoring by checking device status (Up/Down) and provides a responsive interface that automatically refreshes to show current network health.

## Architecture

The system consists of four containerized services working together:

**Flask API (Port 8000)**: Backend API that handles device data retrieval, implements caching strategies, and simulates real-time device status checks. It serves as the data layer, managing connections to MongoDB and Redis.

**Django Dashboard (Port 8080)**: Frontend web application that queries the Flask API and renders device status information in a user-friendly Bootstrap-based interface with automatic refresh capabilities.

**MongoDB (Port 27017)**: Document database storing static device information including device names, IP addresses, locations, and device types. This data changes infrequently and is cached for performance.

**Redis (Port 6379)**: In-memory cache that stores device information to reduce database load and improve response times. Implements a smart caching strategy with appropriate TTL settings.

## Key Features

**Smart Caching Strategy**: Device information is cached in Redis for 5 minutes since it rarely changes, while device status is checked in real-time to ensure accurate monitoring data.

**Fallback Data Handling**: The system gracefully handles failures at any layer, providing fallback data when MongoDB or Redis are unavailable to ensure continuous operation.

**Real-Time Monitoring**: The dashboard auto-refreshes every 5 seconds to display current device status, simulating a network operations center (NOC) display.

**Containerized Architecture**: All services run in Docker containers with proper service dependencies and inter-container communication configured.

**Comprehensive Testing**: Includes both unit tests (isolated function testing with mocked dependencies) and integration tests (full system testing with all services running).

## Technology Stack

**Backend**: Python 3.11, Flask, PyMongo, Redis-py
**Frontend**: Django, Bootstrap 5, Jinja2 templating
**Databases**: MongoDB 7.0, Redis 7.0
**Containerization**: Docker, Docker Compose
**Testing**: pytest, pytest-flask

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- Git (for cloning the repository)

## Installation and Setup

**Clone the repository:**
```bash
git clone https://github.com/RoryHandley/NetworkDashboard.git
```

**Build and start all containers:**
```bash
docker-compose up --build -d
```

This command will build the Flask and Django images, pull the MongoDB and Redis images, and start all services with proper networking configured.

**Verify all containers are running:**
```bash
docker ps
```

You should see four containers: `network_flask_api`, `network_django_dashboard`, `network_mongodb`, and `network_redis`.

## Database Initialization

After starting containers, seed the database:
```bash
docker exec -it network_mongodb mongosh devices --eval 'db.device_info.insertMany([{"id": 1, "name": "Router1", "ip_address": "192.168.1.1"}, {"id": 2, "name": "Switch1", "ip_address": "192.168.1.2"}, {"id": 3, "name": "Firewall1", "ip_address": "192.168.1.3"}])'
```

## Usage

**Access the web dashboard:**
Open your browser and navigate to `http://localhost:8080`

The dashboard displays:
- Overall network health status (All Devices Online or specific device errors)
- Detailed device table showing ID, name, IP address, current status, and last check time
- Color-coded status badges (green for Up, red for Down)
- Automatic refresh every 5 seconds


## Testing

The project includes testing on the flask API with both unit and integration tests.

**Run all tests:**
```bash
cd flask_api
python -m pytest tests/ -v
```

**Run only unit tests:**
```bash
python -m pytest tests/test_unit.py -v
```

**Run only integration tests:**
```bash
python -m pytest tests/test_integration.py -v
```

**Test coverage includes:**
- Unit tests for device status checking functions (with mocked network calls)
- Integration tests for API endpoints with all services running
- Fault tolerance tests (Redis down, MongoDB down, both down scenarios)
- Data validation and required field verification

## Project Structure

```
web_app/
├── docker-compose.yml         # Orchestrates all four services
├── init-mongo.js              # MongoDB initialization script with seed data
├── flask_api/
│   ├── Dockerfile             # Flask API container definition
│   ├── app.py                 # Main Flask application
|   ├── requirements.txt       # Dependencies for Flask container
│   └── tests/
│       ├── test_unit.py       # Unit tests with mocked dependencies
│       └── test_integration.py # Integration tests with live services
├── django_dashboard/
│   ├── Dockerfile             # Django container definition
│   ├── manage.py              # Django management script
│   ├── django_dashboard/      # Django project settings
|   ├── requirements.txt       # Dependencies for Django container
│   └── dashboard/
│       ├── views.py           # View logic for device dashboard
│       ├── urls.py            # URL routing
│       └── templates/
│           └── dashboard.html # Bootstrap-based UI template
|       └── static/
│           └── network.ico    # webpage favicon
└── README.md                  # This file
```


## Docker Configuration

**Service Dependencies:**
- Django dashboard depends on Flask API
- Flask API depends on both MongoDB and Redis
- MongoDB and Redis are independent base services

**Port Mappings:**
- Flask API: 8000:8000
- Django Dashboard: 8080:8080
- MongoDB: 27017:27017
- Redis: 6379:6379

**Networking:**
Containers communicate using Docker's internal DNS. Services reference each other by service name (e.g., Flask connects to MongoDB at `mongodb://mongodb:27017/` rather than localhost).

## Known Platform Differences

**Windows/WSL2 Performance Note:**

If running on Windows with Docker Desktop (which uses WSL2), you may experience slower response times when Redis or MongoDB become unavailable compared to running on macOS or Linux. This is due to WSL2's networking translation layer, which has longer default TCP timeout values for failed connections.

**Symptoms:**
- On macOS/Linux: Failed Redis/MongoDB connections timeout in ~1-3 seconds
- On Windows/WSL2: Failed connections may take 8-16 seconds to timeout


**Workarounds for Windows users:**
- Ensure Redis and MongoDB containers remain running during testing
- Allocate more resources to Docker Desktop (Settings → Resources)
- Consider testing on a Linux VM for production-representative performance

The assessment was developed and tested primarily on macOS where container networking performs optimally.

## Author

Rory Handley 
