from unittest.mock import patch, MagicMock


class TestGovernmentRoutes:
    """Test cases for government routes"""

    def test_get_government_profile_success(self, client, mock_government_data):
        """Test getting a government profile successfully"""
        with patch(
            "routes.government.get_government", return_value=mock_government_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/governments/test-govt-id")

            # Verify response
            assert response.status_code == 200
            assert "account_info" in response.json()
            assert "password" not in response.json()["account_info"]

            # Verify mock was called
            mock_get.assert_called_once_with("test-govt-id")

    def test_get_government_profile_not_found(self, client):
        """Test getting a non-existent government profile"""
        with patch("routes.government.get_government", return_value=None) as mock_get:
            # Send request
            response = client.get("/api/v1/governments/non-existent-id")

            # Verify response is not found
            assert response.status_code == 404
            assert "Government not found" in response.json()["detail"]

            # Verify mock was called
            mock_get.assert_called_once_with("non-existent-id")

    def test_update_government_profile_success(self, client, mock_government_data):
        """Test updating a government profile successfully"""
        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get,
            patch(
                "routes.government.update_government", return_value=True
            ) as mock_update,
        ):
            # Send update request
            update_data = {"name": "Updated Government", "email": "updated@govt.com"}
            response = client.put("/api/v1/governments/test-govt-id", json=update_data)

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Profile updated successfully"

            # Verify mocks were called correctly
            mock_get.assert_called_once_with("test-govt-id")
            mock_update.assert_called_once()

    def test_delete_government_profile_success(self, client, mock_government_data):
        """Test deleting a government profile successfully"""
        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get,
            patch(
                "routes.government.delete_government", return_value=True
            ) as mock_delete,
        ):
            # Send delete request
            response = client.delete("/api/v1/governments/test-govt-id")

            # Verify response
            assert response.status_code == 200
            assert (
                response.json()["message"] == "Government profile deleted successfully"
            )

            # Verify mocks were called
            mock_get.assert_called_once_with("test-govt-id")
            mock_delete.assert_called_once_with("test-govt-id")

    def test_get_wallet_success(self, client, mock_government_data):
        """Test getting wallet information successfully"""
        with patch(
            "routes.government.get_government", return_value=mock_government_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/governments/test-govt-id/wallet")

            # Verify response
            assert response.status_code == 200
            assert "balance" in response.json()
            assert "schemes" in response.json()
            assert "transactions" in response.json()

            # Verify mock was called
            mock_get.assert_called_once_with("test-govt-id")

    def test_get_all_citizens(self, client, mock_government_data, mock_citizen_data):
        """Test getting all citizens"""
        citizens_list = [mock_citizen_data]

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_all_citizens", return_value=citizens_list
            ) as mock_get_citizens,
        ):
            # Send request
            response = client.get("/api/v1/governments/test-govt-id/citizens")

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0
            assert "password" not in response.json()[0]["account_info"]

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_citizens.assert_called_once()

    def test_get_specific_citizen(
        self, client, mock_government_data, mock_citizen_data
    ):
        """Test getting a specific citizen"""
        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_citizen", return_value=mock_citizen_data
            ) as mock_get_citizen,
        ):
            # Send request
            response = client.get(
                "/api/v1/governments/test-govt-id/citizens/test-citizen-id"
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["account_info"]["id"] == "test-citizen-id"
            assert "password" not in response.json()["account_info"]

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_citizen.assert_called_once_with("test-citizen-id")

    def test_get_all_vendors(self, client, mock_government_data, mock_vendor_data):
        """Test getting all vendors"""
        vendors_list = [mock_vendor_data]

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_all_vendors", return_value=vendors_list
            ) as mock_get_vendors,
        ):
            # Send request
            response = client.get("/api/v1/governments/test-govt-id/vendors")

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0
            assert "password" not in response.json()[0]["account_info"]

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_vendors.assert_called_once()

    def test_get_specific_vendor(self, client, mock_government_data, mock_vendor_data):
        """Test getting a specific vendor"""
        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_vendor", return_value=mock_vendor_data
            ) as mock_get_vendor,
        ):
            # Send request
            response = client.get(
                "/api/v1/governments/test-govt-id/vendors/test-vendor-id"
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["account_info"]["id"] == "test-vendor-id"
            assert "password" not in response.json()["account_info"]

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_vendor.assert_called_once_with("test-vendor-id")

    def test_get_all_transactions(
        self, client, mock_government_data, mock_transaction_data
    ):
        """Test getting all transactions"""
        transactions_list = [mock_transaction_data]

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_all_transactions", return_value=transactions_list
            ) as mock_get_transactions,
        ):
            # Send request
            response = client.get("/api/v1/governments/test-govt-id/transactions")

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_transactions.assert_called_once()

    def test_get_specific_transaction(
        self, client, mock_government_data, mock_transaction_data
    ):
        """Test getting a specific transaction"""
        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_transaction", return_value=mock_transaction_data
            ) as mock_get_transaction,
        ):
            # Send request
            response = client.get(
                "/api/v1/governments/test-govt-id/transactions/test-transaction-id"
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["id"] == "test-transaction-id"

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_transaction.assert_called_once_with("test-transaction-id")

    def test_create_scheme_success(
        self, client, mock_government_data, mock_scheme_data
    ):
        """Test creating a scheme successfully"""
        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch("routes.government.Scheme") as mock_scheme_cls,
            patch(
                "routes.government.save_scheme", return_value=True
            ) as mock_save_scheme,
            patch(
                "routes.government.array_union", return_value=True
            ) as mock_array_union,
        ):
            # Configure scheme mock
            scheme_instance = MagicMock()
            scheme_instance.id = "test-scheme-id"
            scheme_instance.to_dict.return_value = mock_scheme_data
            mock_scheme_cls.return_value = scheme_instance

            # Send create request
            scheme_data = {
                "name": "Test Scheme",
                "description": "A test scheme for unit testing",
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
            }
            response = client.post(
                "/api/v1/governments/test-govt-id/schemes", json=scheme_data
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Scheme created successfully"
            assert response.json()["scheme_id"] == "test-scheme-id"

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_scheme_cls.assert_called_once()
            mock_save_scheme.assert_called_once_with("test-scheme-id", mock_scheme_data)
            mock_array_union.assert_called_once()

    def test_get_schemes(self, client, mock_government_data, mock_scheme_data):
        """Test getting schemes created by government"""
        schemes_list = [mock_scheme_data]

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.query_schemes_by_field", return_value=schemes_list
            ) as mock_query_schemes,
        ):
            # Send request
            response = client.get("/api/v1/governments/test-govt-id/schemes")

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0
            assert response.json()[0]["id"] == "test-scheme-id"

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_query_schemes.assert_called_once_with("govt_id", "test-govt-id")

    def test_get_specific_scheme(self, client, mock_government_data, mock_scheme_data):
        """Test getting a specific scheme"""
        # Ensure the scheme belongs to this government
        scheme_data = mock_scheme_data.copy()
        scheme_data["govt_id"] = "test-govt-id"

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_scheme", return_value=scheme_data
            ) as mock_get_scheme,
        ):
            # Send request
            response = client.get(
                "/api/v1/governments/test-govt-id/schemes/test-scheme-id"
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["id"] == "test-scheme-id"
            assert response.json()["govt_id"] == "test-govt-id"

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_scheme.assert_called_once_with("test-scheme-id")

    def test_update_scheme_success(
        self, client, mock_government_data, mock_scheme_data
    ):
        """Test updating a scheme successfully"""
        # Ensure the scheme belongs to this government
        scheme_data = mock_scheme_data.copy()
        scheme_data["govt_id"] = "test-govt-id"

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_scheme", return_value=scheme_data
            ) as mock_get_scheme,
            patch("routes.government.Scheme") as mock_scheme_cls,
            patch(
                "routes.government.save_scheme", return_value=True
            ) as mock_save_scheme,
        ):
            # Configure scheme mock
            scheme_instance = MagicMock()
            scheme_instance.id = "test-scheme-id"
            scheme_instance.to_dict.return_value = scheme_data
            mock_scheme_cls.return_value = scheme_instance

            # Send update request
            scheme_update = {
                "name": "Updated Scheme",
                "description": "An updated test scheme",
                "amount": 6000.0,
                "status": "active",
                "eligibility_criteria": {
                    "occupation": "any",
                    "min_age": 18,
                    "max_age": 60,
                    "gender": "any",
                    "annual_income": 100000.0,
                },
                "tags": ["test", "updated", "scheme"],
            }
            response = client.put(
                "/api/v1/governments/test-govt-id/schemes/test-scheme-id",
                json=scheme_update,
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Scheme updated successfully"
            assert response.json()["scheme_id"] == "test-scheme-id"

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_scheme.assert_called_once_with("test-scheme-id")
            mock_scheme_cls.assert_called_once()
            mock_save_scheme.assert_called_once()

    def test_soft_delete_scheme_success(
        self, client, mock_government_data, mock_scheme_data
    ):
        """Test soft-deleting a scheme successfully"""
        # Ensure the scheme belongs to this government
        scheme_data = mock_scheme_data.copy()
        scheme_data["govt_id"] = "test-govt-id"
        scheme_data["status"] = "active"

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_scheme", return_value=scheme_data
            ) as mock_get_scheme,
            patch(
                "routes.government.save_scheme", return_value=True
            ) as mock_save_scheme,
        ):
            # Send delete request
            response = client.delete(
                "/api/v1/governments/test-govt-id/schemes/test-scheme-id"
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Scheme marked as inactive"

            # Verify mocks were called and status was changed
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_scheme.assert_called_once_with("test-scheme-id")
            # Verify that the saved data has status as inactive
            mock_save_scheme.assert_called_once()
            saved_data = mock_save_scheme.call_args[0][1]
            assert saved_data["status"] == "inactive"

    def test_get_scheme_beneficiaries(
        self, client, mock_government_data, mock_scheme_data, mock_citizen_data
    ):
        """Test getting beneficiaries of a scheme"""
        # Ensure the scheme belongs to this government and has beneficiaries
        scheme_data = mock_scheme_data.copy()
        scheme_data["govt_id"] = "test-govt-id"
        scheme_data["beneficiaries"] = ["test-citizen-id"]

        with (
            patch(
                "routes.government.get_government", return_value=mock_government_data
            ) as mock_get_govt,
            patch(
                "routes.government.get_scheme", return_value=scheme_data
            ) as mock_get_scheme,
            patch(
                "routes.government.get_citizen", return_value=mock_citizen_data
            ) as mock_get_citizen,
        ):
            # Send request
            response = client.get(
                "/api/v1/governments/test-govt-id/schemes/test-scheme-id/beneficiaries"
            )

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0
            assert response.json()[0]["account_info"]["id"] == "test-citizen-id"
            assert "password" not in response.json()[0]["account_info"]

            # Verify mocks were called
            mock_get_govt.assert_called_once_with("test-govt-id")
            mock_get_scheme.assert_called_once_with("test-scheme-id")
            mock_get_citizen.assert_called_once_with("test-citizen-id")
