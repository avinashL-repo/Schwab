# System Health Check API

A FastAPI-based system health monitoring service that evaluates component availability, manages dependency-aware health propagation using a Directed Acyclic Graph (DAG), and visualizes system relationships through an automatically generated graph image.

---

## Features

- REST API built with FastAPI
- DAG-based dependency modelling using NetworkX
- Breadth-First Traversal for dependency ordering
- Async HTTP health checks using `httpx`
- Dependency failure propagation
- Interactive HTML dashboard
- DAG visualization with health-based coloring
- Docker support
- Configurable via JSON payloads
- Terraform Infrastructure-as-Code integration

---

## Project Structure

```bash
project/
│
├── app/
│   ├── graph.py             # DAG creation and traversal logic
│   ├── health.py            # Component health check engine
│   ├── visualization.py     # DAG visualization utility
│   ├── main.py              # FastAPI application entry point
├── Requirements.txt         # Python dependencies
├── Dockerfile               # Docker container setup
├── terraform                # terraform for automated Docker deployment
├── Service JSON.txt         # Sample service dependency input
├── dag.png                  # Generated DAG image (runtime)
└── README.md
```

---

## Architecture Overview

The application models system components as nodes in a Directed Acyclic Graph (DAG).

Each component:
- Has a unique name
- Optionally exposes a health endpoint URL
- May depend on other components

### Dependency Logic

- Components are traversed in dependency order using BFS
- If any dependency becomes unhealthy:
  - Downstream services are automatically marked unhealthy
  - Health checks for blocked services are skipped

This creates cascading dependency awareness across the system.

---

# Core Modules

## 1. `graph.py`

Responsible for:
- Building the DAG
- Validating graph acyclicity
- Traversing dependencies

### Main Functions

#### `build_dag(components)`
Creates a NetworkX Directed Graph from component metadata.

#### `bfs_traversal(G)`
Returns components in dependency-aware traversal order.

---

## 2. `health.py`

Performs asynchronous health checks using HTTP requests.

### Main Function

#### `check_component_health(name, url)`

Logic:
- Sends HTTP GET request
- Status `2xx` → healthy
- Any exception or non-2xx response → unhealthy

Uses:
- `httpx.AsyncClient`
- Timeout handling
- SSL verification

---

## 3. `visualisation.py`

Generates DAG visualizations using Matplotlib and NetworkX.

### Visualization Features

- Green nodes → healthy
- Red nodes → unhealthy
- Directed dependency arrows
- Auto-saved as `dag.png`

---

## 4. `main.py`

Main FastAPI application containing all API endpoints.

### Endpoints

---

## `GET /`

Health service status endpoint.

### Response

```json
{
  "message": "System Health Check API Running"
}
```

---

## `POST /health`

Processes component health checks and dependency evaluation.

### Request Example

```json
{
    "components": [
    {
      "name": "PowerBI_Website",
      "url": "https://app.powerbi.com",
      "depends_on": [
                "Azure_Active_Directory"
      ]
    },
    {
      "name": "Microsoft_Azure",
      "url": "https://azure.microsoft.com/en-gb",
      "depends_on": [
        "Azure_Active_Directory"
      ]}
    ]
}
```

---

### Response Example

```json
{
  "overall_status": "healthy",
  "components": [
    {
      "component": "Azure_Active_Directory",
      "url": "https://entra.microsoft.com",
      "status": "healthy",
      "reason": "http_check",
      "depends_on": []
    },
    {
      "component": "PowerBI_Website",
      "url": "https://app.powerbi.com",
      "status": "healthy",
      "reason": "http_check",
      "depends_on": [
        "Azure_Active_Directory"
      ]
    },
    {
      "component": "Microsoft_Azure",
      "url": "https://azure.microsoft.com/en-gb",
      "status": "healthy",
      "reason": "http_check",
      "depends_on": [
        "Azure_Active_Directory"
      ]
    }
  ]
}
```

---

## `GET /dashboard`

Returns an HTML dashboard displaying:
- Overall system status
- Component status table
- Dependency information

---

## `GET /dag_image`

Returns the generated DAG image.

---

# Installation

## Prerequisites

- Python 3.9+
- pip

---

## Install Dependencies

```bash
pip install -r Requirements.txt
```

---

# Running the Application

## Local Development

```bash
uvicorn main:app --reload
```

Application runs on:

```bash
http://127.0.0.1:8000
```

---

# Using Docker

## Build Docker Image

```bash
docker build -t healthcheckapi .
```

## Run Container

```bash
docker run -p 8000:8000 healthcheckapi
```

---

# Using Terraform

## Terraform-based Infrastructure-as-Code (IaC) simulation

This project includes a local Terraform deployment using the Docker provider to simulate infrastructure provisioning and automated container deployment.

### Terraform Architecture

Terraform
    ↓
Docker Provider
    ↓
Docker Container
    ↓
HealthCheckAPI (FastAPI)

---

## Terraform Deployment Steps

### 1. Build Docker Image

```bash
docker build -t healthcheckapi .
```

### 2. Navigate to Terraform Folder

```bash
cd terraform
```

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Validate Configuration

```bash
terraform validate
```

### 5. Deploy Infrastructure

```bash
terraform apply
```

### 6. Access Application

http://localhost:8000/dashboard

### 7. Destroy Infrastructure

```bash
terraform destroy
```

---


# Example Workflow

## Step 1 — Submit Health Payload

```bash
http://localhost:8000/docs
```

---

## Step 2 — Open Dashboard

```bash
http://localhost:8000/dashboard
```

---

## Step 3 — View DAG Visualization

```bash
http://localhost:8000/dag_image
```

---

# Example Input File

The provided sample file (`Service JSON.txt`) models Microsoft cloud ecosystem dependencies including:

- Azure Active Directory
- Microsoft Azure
- Power BI
- Office 365
- Microsoft Fabric
- Azure Kubernetes Service
- GitHub Enterprise Cloud

This demonstrates real-world dependency propagation.

---

# Dependency Propagation Example

If:

```text
Azure_Active_Directory = unhealthy
```

Then dependent systems automatically become unhealthy:

```text
Microsoft_Azure
PowerBI_Website
Office_365
Microsoft_Intune
Microsoft_Fabric
```

Reason:

```json
"reason": "dependency_failure"
```

---

# Technologies Used

- Python
- FastAPI
- NetworkX
- HTTPX
- Matplotlib
- Uvicorn
- Docker

---


# Notes

- The graph must remain acyclic
- Circular dependencies raise an exception
- DAG image regenerates after each `/health` request
- Health results are cached in memory

---

# Sample Dependency Flow

```text
Azure_Active_Directory
        ↓
Microsoft_Azure
        ↓
PowerBI_Website
        ↓
Microsoft_Fabric
```

# Notes
- This project assumes all component dependencies form a valid Directed Acyclic Graph (DAG) and that each       service exposes a reachable HTTP-based health endpoint.
- Features such as authentication, persistent databases, real-time alerting, and Kubernetes-native integrations were intentionally excluded to keep the solution lightweight, focused, and easy to demonstrate locally.
- The system uses asynchronous health checks, dependency-aware failure propagation, and in-memory state management to balance simplicity, performance, and maintainability.
- Terraform and GitHub Actions integrations are included primarily for simulation and demonstration purposes to showcase Infrastructure-as-Code (IaC) and CI/CD concepts rather than production-grade cloud deployment.
- AI tools were used during development to assist in implementing the solution according to the designed architecture, including support for code refinement, debugging, documentation, and improving overall project structure.

# Author

Avinash Lingam
