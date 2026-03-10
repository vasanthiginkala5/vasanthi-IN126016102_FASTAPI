from fastapi import FastAPI, Query

app = FastAPI()

# --- Temporary data - acting as our database for now -----------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, 'category': 'Electronics', 'in_stock': True},
    {"id": 2, "name": "Notebook", "price": 99, 'category': 'Stationery', 'in_stock': True},
    {"id": 3, "name": "USB Hub", "price": 799, 'category': 'Electronics', 'in_stock': False},
    {"id": 4, "name": "Pen Set", "price": 49, 'category': 'Stationery', 'in_stock': True},

    # Q-1: Add 3 new products to the products list with IDs 5, 6, 7
    {"id": 5, "name": "Laptop Stand", "price": 699, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 1649, "category": "Electronics", "in_stock": False},
    {"id": 7, "name": "Webcam", "price": 1589, "category": "Electronics", "in_stock": True},
]

# ---- Endpoint 0 -- Home -------------------------------------------------
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}

# ---- Endpoint 1 -- Return all products --------------------------------------
@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}

@app.get("/products/filter")
def filter_products(
    category: str = Query(None, description='Electronics  or Stationery'),
    max_price: int = Query(None, description='Maximum price'),
    in_stock: bool = Query(None, description='True = in stock only')
):
    result = products      # start with all products

    if category:
        result = [p for p in result if p['category'] == category]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]   
    
    return {'filtered_products': result, 'count': len(result)}


# ---- Endpoint 4 -- In-Stock Filter --------------------------------------
#Q-3: Show Only In-Stock Products
@app.get("/products/in-stock")
def get_in_stock_products():
    available_products = [p for p in products if p['in_stock'] == True]
    return {"in_stock_products": available_products, "count": len(available_products)}


# --- Endpoint 7 -- Cheapest & Most Expensive Product --------------------------------------
#Q-6(bonus): Cheapest & Most Expensive Product
@app.get("/products/deals")
def product_deals():
    cheapest = min(products, key=lambda p: p['price'])
    most_expensive = max(products, key=lambda p: p['price'])
    return {
        "best_deal": cheapest,
        "premium_pick": most_expensive
    }


# ---- Endpoint 2 -- Return one product by its ID --------------------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"product": product}
    return {"error": "Product not found"} 

# ---- Endpoint 3 -- Category Filter --------------------------------------
#Q-2: Add a Category Filter Endpoint
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "count": len(result)}

# ---- Endpoint 5 -- Store Info --------------------------------------
#Q-4: Build a Store Info Endpoint
@app.get("/store/summary")
def store_summary():
    in_stock_count = len([p for p in products if p['in_stock']])
    out_of_stock_count = len(products) - in_stock_count
    categories = list(set(p['category'] for p in products))
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": categories
    }

# ---- Endpoint 6 -- Search Products --------------------------------------
#Q-5: Search Products by Name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p['name'].lower()]
    if not result:
        return {"message": "No products matched your search"}
    return {"search_keyword": keyword, "products": result, "count": len(result)}


#--- the end of the code ---

#Due to some error the endpoint are not in the correct order. But all endpoints are there and implemented as per the requirements.