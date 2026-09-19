from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="ShopSphere Order API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/ready")
def ready():
    return {
        "status": "ready"
    }


@app.get("/api/products")
def products():
    return [
        {
            "id": 1,
            "name": "Laptop",
            "price": 75000
        },
        {
            "id": 2,
            "name": "Keyboard",
            "price": 2500
        },
        {
            "id": 3,
            "name": "Mouse",
            "price": 1200
        }
    ]


@app.post("/api/orders")
def create_order():
    return {
        "message": "Order created successfully",
        "timestamp": datetime.utcnow().isoformat()
    }