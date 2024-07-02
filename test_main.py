import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_process_receipt():
    receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"}
        ],
        "total": "9.00"
    }
    response = client.post("/receipts/process", json=receipt)
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_points():
    receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"}
        ],
        "total": "9.00"
    }
    process_response = client.post("/receipts/process", json=receipt)
    receipt_id = process_response.json()["id"]

    points_response = client.get(f"/receipts/{receipt_id}/points")
    assert points_response.status_code == 200
    assert points_response.json()["points"] == 109

def test_invalid_receipt():
    invalid_receipt = {
        "retailer": "",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"}
        ],
        "total": "9.00"
    }
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422  # Unprocessable Entity

def test_receipt_not_found():
    response = client.get("/receipts/nonexistent_id/points")
    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"

def test_invalid_date_format():
    invalid_receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "20-03-2022",  # Invalid date format
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"}
        ],
        "total": "9.00"
    }
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_invalid_time_format():
    invalid_receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "2:33 PM",  # Invalid time format
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"}
        ],
        "total": "9.00"
    }
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422

def test_empty_items_list():
    invalid_receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [],  # Empty items list
        "total": "9.00"
    }
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422  # Unprocessable Entity

def test_negative_price():
    invalid_receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "-2.25"}  # Negative price
        ],
        "total": "9.00"
    }
    response = client.post("/receipts/process", json=invalid_receipt)
    assert response.status_code == 422