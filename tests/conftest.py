import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    """Return a TestClient for making API requests"""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing"""
    with patch("db.redis_config.redis_client") as mock_redis:
        yield mock_redis


@pytest.fixture
def mock_citizen_data():
    """Sample citizen data"""
    return {
        "account_info": {
            "id": "test-citizen-id",
            "name": "Test Citizen",
            "email": "test@citizen.com",
            "password": "password123",
            "created_at": "2025-05-10T10:00:00Z",
            "updated_at": "2025-05-10T10:00:00Z",
            "user_type": "citizen",
            "image_url": None,
        },
        "personal_info": {
            "phone": "9876543210",
            "id_type": "Aadhaar",
            "id_number": "123456789012",
            "address": "123 Test Street, Test City",
            "dob": "1990-01-01",
            "gender": "male",
            "occupation": "Software Developer",
            "caste": "General",
            "annual_income": 800000.0,
        },
        "wallet_info": {
            "govt_wallet": {"balance": 5000.0, "transactions": []},
            "personal_wallet": {"balance": 10000.0, "transactions": []},
        },
        "scheme_info": [],
    }


@pytest.fixture
def mock_vendor_data():
    """Sample vendor data"""
    return {
        "account_info": {
            "id": "test-vendor-id",
            "name": "Test Vendor",
            "email": "test@vendor.com",
            "password": "password123",
            "created_at": "2025-05-10T10:00:00Z",
            "updated_at": "2025-05-10T10:00:00Z",
            "user_type": "vendor",
            "gender": "male",
            "image_url": None,
        },
        "business_info": {
            "business_name": "Test Store",
            "business_id": "TEST123456",
            "license_type": "Retail",
            "occupation": "Retailer",
            "phone": "9876543210",
            "address": "456 Business Avenue, Test City",
        },
        "wallet_info": {
            "balance": 50000.0,
            "transactions": [],
        },
    }


@pytest.fixture
def mock_government_data():
    """Sample government data"""
    return {
        "account_info": {
            "id": "test-govt-id",
            "name": "Test Government",
            "email": "test@govt.com",
            "password": "password123",
            "jurisdiction": "Test State",
            "govt_id": "GOVT123456",
            "created_at": "2025-05-10T10:00:00Z",
            "updated_at": "2025-05-10T10:00:00Z",
            "user_type": "government",
            "image_url": None,
        },
        "wallet_info": {
            "balance": 10000000.0,
            "schemes": [],
            "transactions": [],
        },
    }


@pytest.fixture
def mock_scheme_data():
    """Sample scheme data"""
    return {
        "id": "test-scheme-id",
        "name": "Test Scheme",
        "description": "A test scheme for unit testing",
        "govt_id": "test-govt-id",
        "amount": 5000.0,
        "status": "active",
        "eligibility_criteria": {
            "occupation": "any",
            "min_age": 18,
            "max_age": 60,
            "gender": "any",
            "annual_income": 100000.0,
        },
        "tags": ["test", "scheme"],
        "beneficiaries": [],
        "created_at": "2025-05-10T10:00:00Z",
        "updated_at": "2025-05-10T10:00:00Z",
    }


@pytest.fixture
def mock_transaction_data():
    """Sample transaction data"""
    return {
        "id": "test-transaction-id",
        "from_id": "test-citizen-id",
        "to_id": "test-vendor-id",
        "amount": 1000.0,
        "tx_type": "citizen-to-vendor",
        "scheme_id": None,
        "description": "Test transaction",
        "status": "completed",
        "timestamp": "2025-05-10T10:00:00Z",
    }
