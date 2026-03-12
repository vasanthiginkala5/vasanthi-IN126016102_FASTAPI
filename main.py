from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Temporary data — acting as our database for now 
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',        'price': 799,  'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':  49,  'category': 'Stationery',  'in_stock': True },
]

orders = []
order_counter = 0

feedback = []

# ── Pydantic Models for Q3 ────────────────────────────────────
class CustomerFeedback(BaseModel):
    customer_name: str            = Field(..., min_length=2, max_length=100)
    product_id:   int             = Field(..., gt=0)
    rating:       int             = Field(..., ge=1, le=5)
    comment:      Optional[str]   = Field(None, max_length=300)

# ── Pydantic Models for Q5 ────────────────────────────────────
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str           = Field(..., min_length=2)
    contact_email: str           = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_length=1)

# ── Pydantic Model for Orders (Bonus) ─────────────────────────
class OrderRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=10)

@app.get('/')
def home():
    return {'message': 'Welcome to FastAPI Day 2 - Advanced Endpoints'}

# ── Q1: Enhanced Filter with min_price ────────────────────────
@app.get('/products/filter')
def filter_products(
    category:  Optional[str] = Query(None, description='Electronics or Stationery'),
    max_price: Optional[int] = Query(None, description='Maximum price'),
    in_stock:  Optional[bool] = Query(None, description='True = in stock only'),
    min_price: Optional[int] = Query(None, description='Minimum price')
):
    result = products
    
    if category:
        result = [p for p in result if p['category'].lower() == category.lower()]
    
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
    
    return {'filtered_products': result, 'count': len(result)}

# Q2: Get Only Product Name and Price
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    
    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }
    
    return {"error": "Product not found"}

# ── Q3: Customer Feedback Endpoint ───────────────────────────
@app.post('/feedback')
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        'message': 'Feedback submitted successfully',
        'feedback': data.dict(),
        'total_feedback': len(feedback),
    }

# ── Q4: Product Summary Dashboard ────────────────────────────
@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = len([p for p in products if not p["in_stock"]])

    most_expensive_product = max(products, key=lambda p: p["price"])
    cheapest_product = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        },
        "cheapest": {
            "name": cheapest_product["name"],
            "price": cheapest_product["price"]
        },
        "categories": categories
    }

# ── Q5: Bulk Order Processing ────────────────────────────────
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        # find product
        product = next((p for p in products if p["id"] == item.product_id), None)

        # product not found
        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        # out of stock
        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        # calculate subtotal
        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# ── BONUS: Order Status Tracker ──────────────────────────────
@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    order_counter += 1
    
    product = next((p for p in products if p['id'] == order_data.product_id), None)
    
    if not product:
        return {'error': 'Product not found'}
    
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
    
    total_price = product['price'] * order_data.quantity
    
    new_order = {
        'order_id': order_counter,
        'product_id': order_data.product_id,
        'product_name': product['name'],
        'quantity': order_data.quantity,
        'total_price': total_price,
        'status': 'pending'
    }
    
    orders.append(new_order)
    
    return {
        'message': 'Order placed successfully (pending confirmation)',
        'order': new_order
    }

@app.get('/orders/{order_id}')
def get_order(order_id: int):
    for order in orders:
        if order['order_id'] == order_id:
            return {'order': order}
    return {'error': 'Order not found'}

@app.patch('/orders/{order_id}/confirm')
def confirm_order(order_id: int):
    for order in orders:
        if order['order_id'] == order_id:
            order['status'] = 'confirmed'
            return {
                'message': 'Order confirmed',
                'order': order
            }
    return {'error': 'Order not found'}