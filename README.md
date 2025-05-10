# VAUE Observability Project – IT4031 Assignment 02 (2025)

This project demonstrates how to build a REST API with integrated observability using **Prometheus** and **Grafana**, fully containerized with **Docker**.

---

## 📌 Project Components

- **Flask REST API** – A simple service exposing a `/` endpoint and a `/metrics` endpoint.
- **Prometheus** – Pulls metrics from the Flask service.
- **Grafana** – Visualizes the Prometheus metrics on a custom dashboard.
---
##  System Architecture
![ChatGPT Image May 9, 2025, 07_55_50 PM](https://github.com/user-attachments/assets/e4f784d3-30f9-4a38-9ca4-8d1445a4dfc9)


---

## 🧱 File Structure

```
vaue-observability/
├── app/
│   ├── main.py              # Flask app
│   └── Dockerfile           # Container setup
├── prometheus/
│   └── prometheus.yml       # Prometheus config
├── docker-compose.yml       # Docker services
└── README.md                # Project documentation
```

---

## 🚀 How to Run

### Prerequisites
- Docker Desktop installed and running
- 2GB+ free disk space

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/vaue-observability.git
   cd vaue-observability
   ```

2. Run all services:
   ```bash
   docker compose up --build
   ```

3. Access services:
   - Flask API: [http://localhost:5000](http://localhost:5000)
   - Metrics: [http://localhost:5000/metrics](http://localhost:5000/metrics)
   - Prometheus: [http://localhost:9090](http://localhost:9090)
   - Grafana: [http://localhost:3000](http://localhost:3000)

---

## 📊 Grafana Setup

1. Login: `admin` / `admin`
2. Add Prometheus data source:
   - URL: `http://prometheus:9090`
3. Import or create a dashboard:
   - Use `http_requests_total` as a sample query

---

## 🔔 Alerts (Optional)

You can configure alerts in Grafana using thresholds on metrics such as `http_requests_total`.

---

## 📦 Deliverables (for Assignment)

- ✅ Flask API code
- ✅ Dockerfile
- ✅ Prometheus configuration
- ✅ Grafana dashboard (exported JSON)
- ✅ Screenshot of running services (optional)
