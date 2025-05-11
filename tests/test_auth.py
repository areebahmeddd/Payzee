from unittest.mock import patch


class TestAuthRoutes:
    """Test cases for authentication routes"""

    def test_citizen_signup_success(self, client, mock_redis):
        """Test successful citizen signup"""
        # Mock the query and save functions
        with (
            patch("routes.auth.query_citizens_by_field", return_value=[]) as mock_query,
            patch("routes.auth.save_citizen", return_value="test-id") as mock_save,
        ):
            # Send signup request
            response = client.post(
                "/api/v1/auth/signup/citizen",
                json={
                    "name": "John Doe",
                    "password": "password123",
                    "email": "john@example.com",
                    "phone": "9876543210",
                    "id_type": "Aadhaar",
                    "id_number": "123456789012",
                    "address": "123 Main St",
                    "dob": "1990-01-01",
                    "gender": "male",
                    "occupation": "Engineer",
                    "caste": "General",
                    "annual_income": 800000,
                },
            )

            # Verify response
            assert response.status_code == 200
            assert "message" in response.json()
            assert "user_id" in response.json()
            assert response.json()["user_type"] == "citizen"

            # Verify mocks were called
            mock_query.assert_called_once()
            mock_save.assert_called_once()

    def test_citizen_signup_email_exists(self, client):
        """Test citizen signup with existing email"""
        # Mock query to return existing user
        with patch(
            "routes.auth.query_citizens_by_field", return_value=[{"id": "existing-id"}]
        ):
            # Send signup request with existing email
            response = client.post(
                "/api/v1/auth/signup/citizen",
                json={
                    "name": "John Doe",
                    "password": "password123",
                    "email": "existing@example.com",
                    "id_number": "123456789012",
                },
            )

            # Verify response is conflict
            assert response.status_code == 409
            assert "Email already registered" in response.json()["detail"]

    def test_vendor_signup_success(self, client):
        """Test successful vendor signup"""
        # Mock the query and save functions
        with (
            patch("routes.auth.query_vendors_by_field", return_value=[]) as mock_query,
            patch(
                "routes.auth.save_vendor", return_value="test-vendor-id"
            ) as mock_save,
        ):
            # Send signup request
            response = client.post(
                "/api/v1/auth/signup/vendor",
                json={
                    "name": "Store Owner",
                    "password": "password123",
                    "email": "store@example.com",
                    "business_name": "Test Store",
                    "business_id": "STORE123",
                    "license_type": "Retail",
                    "phone": "9876543210",
                    "address": "456 Shop Street",
                },
            )

            # Verify response
            assert response.status_code == 200
            assert "message" in response.json()
            assert "user_id" in response.json()
            assert response.json()["user_type"] == "vendor"

            # Verify mocks were called
            mock_query.assert_called_once()
            mock_save.assert_called_once()

    def test_government_signup_success(self, client):
        """Test successful government signup"""
        # Mock the query and save functions
        with (
            patch(
                "routes.auth.query_governments_by_field", return_value=[]
            ) as mock_query,
            patch(
                "routes.auth.save_government", return_value="test-govt-id"
            ) as mock_save,
        ):
            # Send signup request
            response = client.post(
                "/api/v1/auth/signup/government",
                json={
                    "name": "Local Government",
                    "password": "password123",
                    "email": "govt@example.com",
                    "jurisdiction": "Test District",
                    "govt_id": "GOVT123",
                },
            )

            # Verify response
            assert response.status_code == 200
            assert "message" in response.json()
            assert "user_id" in response.json()
            assert response.json()["user_type"] == "government"

            # Verify mocks were called
            mock_query.assert_called_once()
            mock_save.assert_called_once()

    def test_login_citizen_success(self, client, mock_citizen_data):
        """Test successful citizen login"""
        # Mock query to return citizen
        with patch(
            "routes.auth.query_citizens_by_field", return_value=[mock_citizen_data]
        ) as mock_query:
            # Send login request
            response = client.post(
                "/api/v1/auth/login",
                json={"id_number": "123456789012", "password": "password123"},
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Login successful"
            assert response.json()["user_type"] == "citizen"

            # Verify mock was called
            mock_query.assert_called_once()

    def test_login_vendor_success(self, client, mock_vendor_data):
        """Test successful vendor login"""
        # Mock query to return no citizens but a vendor
        with (
            patch(
                "routes.auth.query_citizens_by_field", return_value=[]
            ) as mock_citizen_query,
            patch(
                "routes.auth.query_vendors_by_field", return_value=[mock_vendor_data]
            ) as mock_vendor_query,
        ):
            # Send login request
            response = client.post(
                "/api/v1/auth/login",
                json={"id_number": "TEST123456", "password": "password123"},
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Login successful"
            assert response.json()["user_type"] == "vendor"

            # Verify mocks were called
            mock_citizen_query.assert_called_once()
            mock_vendor_query.assert_called_once()

    def test_login_government_success(self, client, mock_government_data):
        """Test successful government login"""
        # Mock query to return no citizens or vendors but a government
        with (
            patch(
                "routes.auth.query_citizens_by_field", return_value=[]
            ) as mock_citizen_query,
            patch(
                "routes.auth.query_vendors_by_field", return_value=[]
            ) as mock_vendor_query,
            patch(
                "routes.auth.query_governments_by_field",
                return_value=[mock_government_data],
            ) as mock_govt_query,
        ):
            # Send login request
            response = client.post(
                "/api/v1/auth/login",
                json={"id_number": "GOVT123456", "password": "password123"},
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Login successful"
            assert response.json()["user_type"] == "government"

            # Verify mocks were called
            mock_citizen_query.assert_called_once()
            mock_vendor_query.assert_called_once()
            mock_govt_query.assert_called_once()

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        # Mock query to return no users
        with (
            patch("routes.auth.query_citizens_by_field", return_value=[]),
            patch("routes.auth.query_vendors_by_field", return_value=[]),
            patch("routes.auth.query_governments_by_field", return_value=[]),
        ):
            # Send login request with invalid credentials
            response = client.post(
                "/api/v1/auth/login",
                json={"id_number": "invalid", "password": "wrongpassword"},
            )

            # Verify response is unauthorized
            assert response.status_code == 401
            assert "Invalid ID number or password" in response.json()["detail"]

    def test_logout(self, client):
        """Test logout endpoint"""
        response = client.post("/api/v1/auth/logout")

        # Verify response
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
