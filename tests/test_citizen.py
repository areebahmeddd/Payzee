from fastapi import status
from unittest.mock import patch


class TestCitizenRoutes:
    @patch("routes.citizen.get_citizen")
    def test_get_citizen_profile(self, mock_get_citizen, client, sample_citizen_data):
        # Setup mock
        mock_get_citizen.return_value = sample_citizen_data

        # Make request
        response = client.get("/api/v1/citizens/test-citizen-id")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["account_info"]["name"] == "Test Citizen"
        assert "password" not in response.json()["account_info"]

    @patch("routes.citizen.get_citizen")
    def test_get_citizen_not_found(self, mock_get_citizen, client):
        # Setup mock to return None (citizen not found)
        mock_get_citizen.return_value = None

        # Make request
        response = client.get("/api/v1/citizens/nonexistent-id")

        # Check response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()

    @patch("routes.citizen.get_citizen")
    @patch("routes.citizen.update_citizen")
    def test_update_citizen_profile(
        self, mock_update_citizen, mock_get_citizen, client, sample_citizen_data
    ):
        # Setup mock
        mock_get_citizen.return_value = sample_citizen_data
        mock_update_citizen.return_value = True

        # Update data
        update_data = {"name": "Updated Name", "phone": "9876543210"}

        # Make request
        response = client.put("/api/v1/citizens/test-citizen-id", json=update_data)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Profile updated successfully"

        # Verify update_citizen was called with correct parameters
        mock_update_citizen.assert_called_once()

    @patch("routes.citizen.get_citizen")
    def test_get_wallet(self, mock_get_citizen, client, sample_citizen_data):
        # Setup mock
        mock_get_citizen.return_value = sample_citizen_data

        # Make request
        response = client.get("/api/v1/citizens/test-citizen-id/wallet")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert "govt_wallet" in response.json()
        assert "personal_wallet" in response.json()
        assert response.json()["govt_wallet"]["balance"] == 1000
        assert response.json()["personal_wallet"]["balance"] == 500

    @patch("routes.citizen.get_citizen")
    @patch("routes.citizen.get_vendor")
    @patch("routes.citizen.update_citizen")
    @patch("routes.citizen.update_vendor")
    @patch("routes.citizen.save_transaction")
    @patch("routes.citizen.array_union")
    def test_pay_vendor(
        self,
        mock_array_union,
        mock_save_transaction,
        mock_update_vendor,
        mock_update_citizen,
        mock_get_vendor,
        mock_get_citizen,
        client,
        sample_citizen_data,
        sample_vendor_data,
    ):
        # Setup mocks
        mock_get_citizen.return_value = sample_citizen_data
        mock_get_vendor.return_value = sample_vendor_data

        # Payment data
        payment_data = {
            "vendor_id": "test-vendor-id",
            "amount": 100,
            "wallet_type": "personal_wallet",
            "description": "Test payment",
        }

        # Make request
        response = client.post(
            "/api/v1/citizens/test-citizen-id/pay", json=payment_data
        )

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert "transaction_id" in response.json()

        # Verify functions were called
        mock_update_citizen.assert_called_once()
        mock_update_vendor.assert_called_once()
        mock_save_transaction.assert_called_once()
        assert mock_array_union.call_count == 2  # Once for citizen, once for vendor

    @patch("routes.citizen.get_citizen")
    @patch("routes.citizen.query_transactions_by_field")
    def test_get_transactions(
        self,
        mock_query_transactions,
        mock_get_citizen,
        client,
        sample_citizen_data,
        sample_transaction_data,
    ):
        # Setup mocks
        mock_get_citizen.return_value = sample_citizen_data
        # Return the transaction twice (as if it's both sent and received)
        mock_query_transactions.side_effect = [[sample_transaction_data], []]

        # Make request
        response = client.get("/api/v1/citizens/test-citizen-id/transactions")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == "test-transaction-id"

    @patch("routes.citizen.get_citizen")
    @patch("routes.citizen.get_scheme")
    @patch("routes.citizen.array_union")
    def test_enroll_scheme(
        self,
        mock_array_union,
        mock_get_scheme,
        mock_get_citizen,
        client,
        sample_citizen_data,
        sample_scheme_data,
    ):
        # Setup mocks
        mock_get_citizen.return_value = sample_citizen_data
        mock_get_scheme.return_value = sample_scheme_data
        mock_array_union.return_value = True

        # Make request
        response = client.post(
            "/api/v1/citizens/test-citizen-id/enroll-scheme/test-scheme-id"
        )

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully enrolled in scheme"

        # Verify array_union was called
        mock_array_union.assert_called_once_with(
            "schemes:", "test-scheme-id", "beneficiaries", ["test-citizen-id"]
        )
