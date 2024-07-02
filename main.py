from typing import Dict
from fastapi import Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel, constr, conlist, condecimal
from uuid import uuid4
from datetime import date, time
import math

app = FastAPI()

# In-memory storage for receipts
receipts: Dict[str, int] = {}

class Item(BaseModel):
    shortDescription: constr(min_length=1, max_length=255)  # Alphanumeric, spaces, and hyphens
    price: condecimal(gt=0, decimal_places=2)  # Decimal with two places, greater than 0

class Receipt(BaseModel):
    retailer: constr(min_length=1, max_length=255)  # Alphanumeric, spaces, hyphens, and ampersands
    purchaseDate: date  # Date in YYYY-MM-DD format
    purchaseTime: time  # Time in HH:MM format
    items: conlist(Item, min_length=1)  # List of items with at least one item
    total: condecimal(gt=0, decimal_places=2)  # Decimal with two places, greater than 0

class ReceiptResponse(BaseModel):
    id: constr(min_length=1)  # Non-whitespace string

class PointsResponse(BaseModel):
    points: int

def calculate_points(receipt: Receipt) -> int:
    """
    Calculate points for a given receipt based on predefined rules.
    """
    points = 0
    
    # Rule 1: One point for every alphanumeric character in the retailer name
    points += sum(c.isalnum() for c in receipt.retailer)

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    if float(receipt.total).is_integer():
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if float(receipt.total) % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    points += (len(receipt.items) // 2) * 5

    # Rule 5: Points based on item description length
    for item in receipt.items:
        if len(item.shortDescription.strip()) % 3 == 0:
            points += math.ceil(float(item.price) * 0.2)

    # Rule 6: 6 points if the day in the purchase date is odd
    if receipt.purchaseDate.day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    if 14 <= receipt.purchaseTime.hour < 16:
        points += 10
    return points

@app.post("/receipts/process", response_model=ReceiptResponse)
def process_receipt(receipt: Receipt, db: Dict[str, int] = Depends(lambda: receipts)) -> ReceiptResponse:
    """
    Process a receipt and store the calculated points.
    """
    receipt_id = str(uuid4())
    points = calculate_points(receipt)
    db[receipt_id] = points
    return ReceiptResponse(id=receipt_id)

@app.get("/receipts/{id}/points", response_model=PointsResponse)
def get_points(id: str = Path(..., min_length=1), db: Dict[str, int] = Depends(lambda: receipts)) -> PointsResponse:
    """
    Retrieve the points for a given receipt ID.
    """
    if id not in db:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return PointsResponse(points=db[id])