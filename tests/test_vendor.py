from unittest.mock import patch


class TestVendorRoutes:
    """Test cases for vendor routes"""

    def test_get_vendor_profile_success(self, client, mock_vendor_data):
        """Test getting a vendor profile successfully"""
        with patch(
            "routes.vendor.get_vendor", return_value=mock_vendor_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/vendors/test-vendor-id")

            # Verify response
            assert response.status_code == 200
            assert "account_info" in response.json()
            assert "password" not in response.json()["account_info"]

            # Verify mock was called
            mock_get.assert_called_once_with("test-vendor-id")

    def test_get_vendor_profile_not_found(self, client):
        """Test getting a non-existent vendor profile"""
        with patch("routes.vendor.get_vendor", return_value=None) as mock_get:
            # Send request
            response = client.get("/api/v1/vendors/non-existent-id")

            # Verify response is not found
            assert response.status_code == 404
            assert "Vendor not found" in response.json()["detail"]

            # Verify mock was called
            mock_get.assert_called_once_with("non-existent-id")

    def test_update_vendor_profile_success(self, client, mock_vendor_data):
        """Test updating a vendor profile successfully"""
        with (
            patch(
                "routes.vendor.get_vendor", return_value=mock_vendor_data
            ) as mock_get,
            patch("routes.vendor.update_vendor", return_value=True) as mock_update,
        ):
            # Send update request
            update_data = {"name": "Updated Vendor", "email": "updated@vendor.com"}
            response = client.put("/api/v1/vendors/test-vendor-id", json=update_data)

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Profile updated successfully"

            # Verify mocks were called correctly
            mock_get.assert_called_once_with("test-vendor-id")
            mock_update.assert_called_once()

    def test_update_vendor_profile_not_found(self, client):
        """Test updating a non-existent vendor profile"""
        with patch("routes.vendor.get_vendor", return_value=None) as mock_get:
            # Send update request
            update_data = {"name": "Updated Vendor"}
            response = client.put("/api/v1/vendors/non-existent-id", json=update_data)

            # Verify response is not found
            assert response.status_code == 404
            assert "Vendor not found" in response.json()["detail"]

            # Verify mock was called
            mock_get.assert_called_once_with("non-existent-id")

    def test_delete_vendor_profile_success(self, client, mock_vendor_data):
        """Test deleting a vendor profile successfully"""
        with (
            patch(
                "routes.vendor.get_vendor", return_value=mock_vendor_data
            ) as mock_get,
            patch("routes.vendor.delete_vendor", return_value=True) as mock_delete,
        ):
            # Send delete request
            response = client.delete("/api/v1/vendors/test-vendor-id")

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Vendor profile deleted successfully"

            # Verify mocks were called
            mock_get.assert_called_once_with("test-vendor-id")
            mock_delete.assert_called_once_with("test-vendor-id")

    def test_get_wallet_success(self, client, mock_vendor_data):
        """Test getting wallet information successfully"""
        with patch(
            "routes.vendor.get_vendor", return_value=mock_vendor_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/vendors/test-vendor-id/wallet")

            # Verify response
            assert response.status_code == 200
            assert "balance" in response.json()
            assert "transactions" in response.json()

            # Verify mock was called
            mock_get.assert_called_once_with("test-vendor-id")

    def test_generate_qr_success(self, client, mock_vendor_data):
        """Test generating QR code successfully"""
        with patch(
            "routes.vendor.get_vendor", return_value=mock_vendor_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/vendors/test-vendor-id/generate-qr")

            # Verify response
            assert response.status_code == 200
            assert "qr_code" in response.json()
            assert "user_id" in response.json()
            assert response.json()["user_id"] == "test-vendor-id"

            # Verify mock was called
            mock_get.assert_called_once_with("test-vendor-id")

    def test_get_transactions(self, client, mock_transaction_data):
        """Test getting transaction history"""
        transaction_list = [mock_transaction_data]

        # Mock query functions to return transactions
        with patch("routes.vendor.query_transactions_by_field") as mock_query:
            # Configure mock to return different values based on arguments
            mock_query.side_effect = (
                lambda field, value: transaction_list
                if value == "test-vendor-id"
                else []
            )

            # Send request
            response = client.get("/api/v1/vendors/test-vendor-id/transactions")

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0

            # Verify mock was called twice (for from_id and to_id)
            assert mock_query.call_count == 2

    def test_get_specific_transaction_success(
        self, client, mock_vendor_data, mock_transaction_data
    ):
        """Test getting a specific transaction"""
        # Set the vendor as a participant in the transaction
        transaction_data = mock_transaction_data.copy()
        transaction_data["to_id"] = "test-vendor-id"

        with (
            patch(
                "routes.vendor.get_vendor", return_value=mock_vendor_data
            ) as mock_get_vendor,
            patch(
                "routes.vendor.get_transaction", return_value=transaction_data
            ) as mock_get_transaction,
        ):
            # Send request
            response = client.get(
                "/api/v1/vendors/test-vendor-id/transactions/test-transaction-id"
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["id"] == "test-transaction-id"
            assert response.json()["to_id"] == "test-vendor-id"

            # Verify mocks were called
            mock_get_vendor.assert_called_once_with("test-vendor-id")
            mock_get_transaction.assert_called_once_with("test-transaction-id")

    def test_get_specific_transaction_not_associated(
        self, client, mock_vendor_data, mock_transaction_data
    ):
        """Test getting a transaction not associated with the vendor"""
        # Ensure the vendor is not a participant in the transaction
        transaction_data = mock_transaction_data.copy()
        transaction_data["from_id"] = "other-id"
        transaction_data["to_id"] = "other-id-2"

        with (
            patch(
                "routes.vendor.get_vendor", return_value=mock_vendor_data
            ) as mock_get_vendor,
            patch(
                "routes.vendor.get_transaction", return_value=transaction_data
            ) as mock_get_transaction,
        ):
            # Send request
            response = client.get(
                "/api/v1/vendors/test-vendor-id/transactions/test-transaction-id"
            )

            # Verify response is forbidden
            assert response.status_code == 403
            assert "not associated with this vendor" in response.json()["detail"]

            # Verify mocks were called
            mock_get_vendor.assert_called_once_with("test-vendor-id")
            mock_get_transaction.assert_called_once_with("test-transaction-id")
