from fastapi import status
from unittest.mock import patch


class TestAuthRoutes:
    @patch("routes.auth.query_citizens_by_field")
    @patch("routes.auth.save_citizen")
    def test_citizen_signup(self, mock_save_citizen, mock_query, client):
        # Configure mock to return empty list (no existing user)
        mock_query.return_value = []

        # Test data
        signup_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "phone": "1234567890",
            "address": "123 Test St",
            "id_proof": "ABC123",
        }

        # Send request to the endpoint
        response = client.post("/api/v1/auth/signup/citizen", json=signup_data)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert "user_id" in response.json()
        assert response.json()["user_type"] == "citizen"
        assert "message" in response.json()

        # Verify save_citizen was called
        mock_save_citizen.assert_called_once()

    @patch("routes.auth.query_citizens_by_field")
    def test_citizen_signup_existing_email(self, mock_query, client):
        # Configure mock to return a user (email already exists)
        mock_query.return_value = [{"account_info": {"email": "existing@example.com"}}]

        # Test data
        signup_data = {
            "name": "Test User",
            "email": "existing@example.com",
            "password": "password123",
        }

        # Send request to the endpoint
        response = client.post("/api/v1/auth/signup/citizen", json=signup_data)

        # Check response
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "detail" in response.json()

    @patch("routes.auth.query_vendors_by_field")
    @patch("routes.auth.save_vendor")
    def test_vendor_signup(self, mock_save_vendor, mock_query, client):
        # Configure mock to return empty list (no existing user)
        mock_query.return_value = []

        # Test data
        signup_data = {
            "name": "Vendor Name",
            "email": "vendor@example.com",
            "password": "password123",
            "business_name": "Test Business",
        }

        # Send request to the endpoint
        response = client.post("/api/v1/auth/signup/vendor", json=signup_data)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert "user_id" in response.json()
        assert response.json()["user_type"] == "vendor"

        # Verify save_vendor was called
        mock_save_vendor.assert_called_once()

    @patch("routes.auth.query_citizens_by_field")
    @patch("routes.auth.query_vendors_by_field")
    @patch("routes.auth.query_governments_by_field")
    def test_login_success_citizen(
        self, mock_query_govts, mock_query_vendors, mock_query_citizens, client
    ):
        # Only citizens query returns a result
        mock_query_citizens.return_value = [
            {
                "account_info": {
                    "id": "test-id-123",
                    "email": "user@example.com",
                    "password": "password123",
                }
            }
        ]
        mock_query_vendors.return_value = []
        mock_query_govts.return_value = []

        # Login data
        login_data = {"email": "user@example.com", "password": "password123"}

        # Send login request
        response = client.post("/api/v1/auth/login", json=login_data)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] == "test-id-123"
        assert response.json()["user_type"] == "citizen"

    @patch("routes.auth.query_citizens_by_field")
    @patch("routes.auth.query_vendors_by_field")
    @patch("routes.auth.query_governments_by_field")
    def test_login_invalid_credentials(
        self, mock_query_govts, mock_query_vendors, mock_query_citizens, client
    ):
        # Queries return results but with wrong password
        mock_query_citizens.return_value = [
            {
                "account_info": {
                    "id": "test-id-123",
                    "email": "user@example.com",
                    "password": "correct_password",
                }
            }
        ]
        mock_query_vendors.return_value = []
        mock_query_govts.return_value = []

        # Login with wrong password
        login_data = {"email": "user@example.com", "password": "wrong_password"}

        # Send login request
        response = client.post("/api/v1/auth/login", json=login_data)

        # Check response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
