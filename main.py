from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="My FastAPI Server", version="1.0.0")

# Pydantic models
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

# In-memory storage (for demo purposes)
items_db = {}
users_db = {}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!", "timestamp": datetime.now().isoformat()}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Items endpoints
@app.post("/items/")
async def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item.dict()
    return {"id": item_id, **item.dict()}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items_db[item_id]}

@app.get("/items/")
async def list_items(skip: int = 0, limit: int = 10):
    items_list = []
    for item_id, item in items_db.items():
        if skip <= item_id - 1 < skip + limit:
            items_list.append({"id": item_id, **item})
    return {"items": items_list, "total": len(items_db)}

# Users endpoints
@app.post("/users/")
async def create_user(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[user.username] = user.dict()
    return {"username": user.username, **user.dict()}

@app.get("/users/{username}")
async def get_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[username]

# Example with query parameters
@app.get("/calculate")
async def calculate(a: float, b: float, operation: str = "add"):
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else None
    }

    if operation not in operations:
        raise HTTPException(status_code=400, detail="Invalid operation. Use: add, subtract, multiply, or divide")

    result = operations[operation]
    if result is None:
        raise HTTPException(status_code=400, detail="Division by zero")

    return {"a": a, "b": b, "operation": operation, "result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)