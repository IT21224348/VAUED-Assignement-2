import time
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, Gauge, Summary, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from waitress import serve

# --- Prometheus Metrics ---
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests made to the application.",
    ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "endpoint"]
)
IN_PROGRESS_REQUESTS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently in progress.",
    ["method", "endpoint"]
)
RESPONSE_SIZE_BYTES = Summary(
    "http_response_size_bytes",
    "HTTP response size in bytes.",
    ["method", "endpoint"]
)
HTTP_ERROR_COUNT = Counter(
    "http_errors_total",
    "Total number of failed HTTP requests.",
    ["method", "endpoint", "status_code"]
)

# --- Flask Application ---
app = Flask(__name__)

items = [
    {"id": 1, "name": "item1", "value": 100},
    {"id": 2, "name": "item2", "value": 200}
]
next_item_id = 3

def record_metrics(method, endpoint, start_time, response_size):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
    RESPONSE_SIZE_BYTES.labels(method=method, endpoint=endpoint).observe(response_size)

@app.route("/api/items", methods=["GET"])
def get_items():
    start_time = time.time()
    endpoint = "/api/items"
    IN_PROGRESS_REQUESTS.labels(method="GET", endpoint=endpoint).inc()
    try:
        response = jsonify(items)
        record_metrics("GET", endpoint, start_time, len(response.get_data()))
        return response, 200
    finally:
        IN_PROGRESS_REQUESTS.labels(method="GET", endpoint=endpoint).dec()

@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    start_time = time.time()
    endpoint = "/api/items/<id>"
    IN_PROGRESS_REQUESTS.labels(method="GET", endpoint=endpoint).inc()
    try:
        item = next((item for item in items if item["id"] == item_id), None)
        if item:
            response = jsonify(item)
            record_metrics("GET", endpoint, start_time, len(response.get_data()))
            return response, 200
        else:
            response = jsonify({"error": "Item not found"})
            record_metrics("GET", endpoint, start_time, len(response.get_data()))
            HTTP_ERROR_COUNT.labels(method="GET", endpoint=endpoint, status_code="404").inc()
            return response, 404
    finally:
        IN_PROGRESS_REQUESTS.labels(method="GET", endpoint=endpoint).dec()

@app.route("/api/items", methods=["POST"])
def create_item():
    start_time = time.time()
    endpoint = "/api/items"
    IN_PROGRESS_REQUESTS.labels(method="POST", endpoint=endpoint).inc()
    try:
        global next_item_id
        if not request.json or "name" not in request.json or "value" not in request.json:
            response = jsonify({"error": "Missing name or value in request body"})
            record_metrics("POST", endpoint, start_time, len(response.get_data()))
            HTTP_ERROR_COUNT.labels(method="POST", endpoint=endpoint, status_code="400").inc()
            return response, 400

        new_item = {
            "id": next_item_id,
            "name": request.json["name"],
            "value": request.json["value"]
        }
        items.append(new_item)
        next_item_id += 1
        response = jsonify(new_item)
        record_metrics("POST", endpoint, start_time, len(response.get_data()))
        return response, 201
    finally:
        IN_PROGRESS_REQUESTS.labels(method="POST", endpoint=endpoint).dec()

@app.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    start_time = time.time()
    endpoint = "/api/items/<id>"
    IN_PROGRESS_REQUESTS.labels(method="PUT", endpoint=endpoint).inc()
    try:
        item = next((item for item in items if item["id"] == item_id), None)
        if not item:
            response = jsonify({"error": "Item not found"})
            record_metrics("PUT", endpoint, start_time, len(response.get_data()))
            HTTP_ERROR_COUNT.labels(method="PUT", endpoint=endpoint, status_code="404").inc()
            return response, 404

        if not request.json:
            response = jsonify({"error": "Request body is missing"})
            record_metrics("PUT", endpoint, start_time, len(response.get_data()))
            HTTP_ERROR_COUNT.labels(method="PUT", endpoint=endpoint, status_code="400").inc()
            return response, 400

        item["name"] = request.json.get("name", item["name"])
        item["value"] = request.json.get("value", item["value"])
        response = jsonify(item)
        record_metrics("PUT", endpoint, start_time, len(response.get_data()))
        return response, 200
    finally:
        IN_PROGRESS_REQUESTS.labels(method="PUT", endpoint=endpoint).dec()

@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    start_time = time.time()
    endpoint = "/api/items/<id>"
    IN_PROGRESS_REQUESTS.labels(method="DELETE", endpoint=endpoint).inc()
    try:
        global items
        initial_len = len(items)
        items = [item for item in items if item["id"] != item_id]
        if len(items) < initial_len:
            response = jsonify({"message": "Item deleted"})
            record_metrics("DELETE", endpoint, start_time, len(response.get_data()))
            return response, 200
        else:
            response = jsonify({"error": "Item not found"})
            record_metrics("DELETE", endpoint, start_time, len(response.get_data()))
            HTTP_ERROR_COUNT.labels(method="DELETE", endpoint=endpoint, status_code="404").inc()
            return response, 404
    finally:
        IN_PROGRESS_REQUESTS.labels(method="DELETE", endpoint=endpoint).dec()

# Simulate Internal Server Error
@app.route("/api/crash", methods=["GET"])
def crash():
    raise Exception("Simulated server error")

@app.errorhandler(Exception)
def handle_exception(e):
    HTTP_ERROR_COUNT.labels(method=request.method, endpoint=request.path, status_code="500").inc()
    return jsonify({"error": "Internal Server Error"}), 500

# Prometheus middleware to expose /metrics
app_dispatch = DispatcherMiddleware(app, {
    "/metrics": make_wsgi_app()
})

if __name__ == "__main__":
    serve(app_dispatch, host="0.0.0.0", port=5000)
