import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product_schema import ProductDetails

def test_product_schema_validation():
    """Test ProductDetails schema validation"""
    # Valid product
    product = ProductDetails(
        product_name="Test Product",
        price=99.99,
        currency="USD",
        features=["feature1", "feature2"],
        brand="Test Brand",
        rating=4.5
    )
    assert product.product_name == "Test Product"
    assert product.price == 99.99
    assert product.currency == "USD"
    assert len(product.features) == 2
    assert product.brand == "Test Brand"
    assert product.rating == 4.5

def test_product_schema_optional_fields():
    """Test ProductDetails with optional fields"""
    product = ProductDetails(
        product_name="Test Product",
        price=50.0,
        currency="EUR",
        features=["feature1"]
    )
    assert product.product_name == "Test Product"
    assert product.brand is None
    assert product.rating is None

def test_product_schema_rating_validation():
    """Test rating validation (must be between 1.0 and 5.0)"""
    # Valid rating
    product = ProductDetails(
        product_name="Test",
        price=10.0,
        currency="USD",
        features=[],
        rating=3.5
    )
    assert product.rating == 3.5
    
    # Invalid rating (too high)
    with pytest.raises(Exception):
        ProductDetails(
            product_name="Test",
            price=10.0,
            currency="USD",
            features=[],
            rating=6.0
        )
    
    # Invalid rating (too low)
    with pytest.raises(Exception):
        ProductDetails(
            product_name="Test",
            price=10.0,
            currency="USD",
            features=[],
            rating=0.5
        )

def test_metrics_file_creation():
    """Test that metrics file can be created"""
    metrics_file = "metrics.json"
    if os.path.exists(metrics_file):
        os.remove(metrics_file)
    
    test_metrics = {
        "total_requests": 0,
        "successful_extractions": 0,
        "failed_extractions": 0,
        "validation_errors": 0,
        "total_latency_ms": 0,
        "average_latency_ms": 0.0,
        "last_request_time": None,
        "requests": []
    }
    
    with open(metrics_file, 'w') as f:
        json.dump(test_metrics, f)
    
    assert os.path.exists(metrics_file)
    
    with open(metrics_file, 'r') as f:
        loaded = json.load(f)
        assert loaded["total_requests"] == 0
