import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch("db.redis_config.redis_client") as mock_client:
        yield mock_client


@pytest.fixture
def sample_citizen_data():
    return {
        "account_info": {
            "id": "test-citizen-id",
            "name": "Test Citizen",
            "email": "citizen@example.com",
            "password": "password123",
            "user_type": "citizen",
        },
        "personal_info": {
            "phone": "+91 9876543210",
            "address": "Test Address",
            "id_type": "Aadhaar",
            "id_number": "123456789012",
        },
        "wallet_info": {
            "govt_wallet": {"balance": 1000, "transactions": []},
            "personal_wallet": {"balance": 500, "transactions": []},
        },
    }


@pytest.fixture
def sample_vendor_data():
    return {
        "account_info": {
            "id": "test-vendor-id",
            "name": "Test Vendor",
            "email": "vendor@example.com",
            "password": "password123",
            "user_type": "vendor",
        },
        "business_info": {
            "business_name": "Test Business",
            "phone": "+91 9988776655",
            "address": "Test Address",
            "business_id": "GSTIN22AAAAA1111Z",
            "license_type": "private",
        },
        "wallet_info": {"balance": 2000, "transactions": []},
    }


@pytest.fixture
def sample_government_data():
    return {
        "account_info": {
            "id": "test-govt-id",
            "name": "Test Government",
            "email": "govt@example.com",
            "password": "password123",
            "department": "Test Department",
            "jurisdiction": "Test Jurisdiction",
            "user_type": "government",
        },
        "wallet_info": {"balance": 10000, "schemes": [], "transactions": []},
    }


@pytest.fixture
def sample_scheme_data():
    return {
        "id": "test-scheme-id",
        "name": "Test Scheme",
        "description": "A test scheme",
        "govt_id": "test-govt-id",
        "amount": 1000,
        "eligibility_criteria": {"age": {"min": 18}},
        "beneficiaries": [],
        "status": "active",
    }


@pytest.fixture
def sample_transaction_data():
    return {
        "id": "test-transaction-id",
        "from_id": "test-govt-id",
        "to_id": "test-citizen-id",
        "amount": 500,
        "tx_type": "government-to-citizen",
        "scheme_id": "test-scheme-id",
        "description": "Test transaction",
        "status": "completed",
        "timestamp": "2025-05-03T12:00:00",
    }
