from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os
import json
import time
import psycopg2
import redis
app = FastAPI(
    title="ShopSphere Order API",
    version="2.0.0"
)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "shopsphere")
DB_USER = os.getenv("DB_USER", "shopsphere")
DB_PASSWORD = os.getenv("DB_PASSWORD", "shopsphere123")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        decode_responses=True
    )
class OrderRequest(BaseModel):
    product_id: int
    quantity: int
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
@app.get("/ready")
def ready():
    try:
        conn = get_db_connection()
        conn.close()
        redis_client = get_redis_client()
        redis_client.ping()
        return {
            "status": "ready"
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Dependencies unavailable: {str(exc)}"
        )
@app.get("/api/products")
def get_products():
    cache_key = "shopsphere:products"
    try:
        redis_client = get_redis_client()
        cached_products = redis_client.get(cache_key)
        if cached_products:
            return json.loads(cached_products)
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, price, description
        FROM products
        ORDER BY id
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    products = [
        {
            "id": row[0],
            "name": row[1],
            "price": float(row[2]),
            "description": row[3]
        }
        for row in rows
    ]
    try:
        redis_client = get_redis_client()
        redis_client.setex(
            cache_key,
            60,
            json.dumps(products)
        )
    except Exception:
        pass
    return products
@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, price, description
        FROM products
        WHERE id = %s
        """,
        (product_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    return {
        "id": row[0],
        "name": row[1],
        "price": float(row[2]),
        "description": row[3]
    }
@app.post("/api/orders")
def create_order(order: OrderRequest):
    if order.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM products
        WHERE id = %s
        """,
        (order.product_id,)
    )
    product = cursor.fetchone()
    if product is None:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    cursor.execute(
        """
        INSERT INTO orders
            (product_id, quantity, status, created_at)
        VALUES
            (%s, %s, %s, %s)
        RETURNING id, product_id, quantity,
                  status, created_at
        """,
        (
            order.product_id,
            order.quantity,
            "CREATED",
            datetime.utcnow()
        )
    )
    created_order = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {
        "id": created_order[0],
        "product_id": created_order[1],
        "quantity": created_order[2],
        "status": created_order[3],
        "created_at": created_order[4].isoformat()
    }
@app.get("/api/orders")
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            id,
            product_id,
            quantity,
            status,
            created_at
        FROM orders
        ORDER BY id DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": row[0],
            "product_id": row[1],
            "quantity": row[2],
            "status": row[3],
            "created_at": row[4].isoformat()
        }
        for row in rows
    ]