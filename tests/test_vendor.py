from fastapi import status
from unittest.mock import patch


class TestVendorRoutes:
    @patch("routes.vendor.get_vendor")
    def test_get_vendor_profile(self, mock_get_vendor, client, sample_vendor_data):
        # Setup mock
        mock_get_vendor.return_value = sample_vendor_data

        # Make request
        response = client.get("/api/v1/vendors/test-vendor-id")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["account_info"]["name"] == "Test Vendor"
        assert "password" not in response.json()["account_info"]

    @patch("routes.vendor.get_vendor")
    def test_get_vendor_not_found(self, mock_get_vendor, client):
        # Setup mock to return None (vendor not found)
        mock_get_vendor.return_value = None

        # Make request
        response = client.get("/api/v1/vendors/nonexistent-id")

        # Check response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()

    @patch("routes.vendor.get_vendor")
    @patch("routes.vendor.update_vendor")
    def test_update_vendor_profile(
        self, mock_update_vendor, mock_get_vendor, client, sample_vendor_data
    ):
        # Setup mock
        mock_get_vendor.return_value = sample_vendor_data
        mock_update_vendor.return_value = True

        # Update data
        update_data = {"name": "Updated Business Name", "phone": "9876543210"}

        # Make request
        response = client.put("/api/v1/vendors/test-vendor-id", json=update_data)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Profile updated successfully"

        # Verify update_vendor was called with correct parameters
        mock_update_vendor.assert_called_once()

    @patch("routes.vendor.get_vendor")
    def test_get_wallet(self, mock_get_vendor, client, sample_vendor_data):
        # Setup mock
        mock_get_vendor.return_value = sample_vendor_data

        # Make request
        response = client.get("/api/v1/vendors/test-vendor-id/wallet")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["balance"] == 2000

    @patch("routes.vendor.get_vendor")
    @patch("routes.vendor.query_transactions_by_field")
    def test_get_transactions(
        self,
        mock_query_transactions,
        mock_get_vendor,
        client,
        sample_vendor_data,
        sample_transaction_data,
    ):
        # Setup mocks
        mock_get_vendor.return_value = sample_vendor_data
        # Return the transaction twice (as if it's both sent and received)
        mock_query_transactions.side_effect = [[sample_transaction_data], []]

        # Make request
        response = client.get("/api/v1/vendors/test-vendor-id/transactions")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == "test-transaction-id"

    @patch("routes.vendor.get_vendor")
    def test_generate_qr(self, mock_get_vendor, client, sample_vendor_data):
        # Setup mock
        mock_get_vendor.return_value = sample_vendor_data

        # Make request
        response = client.get("/api/v1/vendors/test-vendor-id/generate-qr")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert "qr_code" in response.json()
        assert "user_id" in response.json()
        assert response.json()["user_id"] == "test-vendor-id"
