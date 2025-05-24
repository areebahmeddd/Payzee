from unittest.mock import patch, MagicMock


class TestCitizenRoutes:
    def test_get_citizen_profile_success(self, client, mock_citizen_data):
        with patch(
            "routes.citizen.get_citizen", return_value=mock_citizen_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/citizens/test-citizen-id")

            # Verify response
            assert response.status_code == 200
            assert "account_info" in response.json()
            assert "password" not in response.json()["account_info"]

            # Verify mock was called
            mock_get.assert_called_once_with("test-citizen-id")

    def test_get_citizen_profile_not_found(self, client):
        with patch("routes.citizen.get_citizen", return_value=None) as mock_get:
            # Send request
            response = client.get("/api/v1/citizens/non-existent-id")

            # Verify response is not found
            assert response.status_code == 404
            assert "Citizen not found" in response.json()["detail"]

            # Verify mock was called
            mock_get.assert_called_once_with("non-existent-id")

    def test_update_citizen_profile_success(self, client, mock_citizen_data):
        with (
            patch(
                "routes.citizen.get_citizen", return_value=mock_citizen_data
            ) as mock_get,
            patch("routes.citizen.update_citizen", return_value=True) as mock_update,
        ):
            # Send update request
            update_data = {"name": "Updated Name", "email": "updated@example.com"}
            response = client.put("/api/v1/citizens/test-citizen-id", json=update_data)

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Profile updated successfully"

            # Verify mocks were called correctly
            mock_get.assert_called_once_with("test-citizen-id")
            mock_update.assert_called_once()

    def test_update_citizen_profile_not_found(self, client):
        with patch("routes.citizen.get_citizen", return_value=None) as mock_get:
            # Send update request
            update_data = {"name": "Updated Name"}
            response = client.put("/api/v1/citizens/non-existent-id", json=update_data)

            # Verify response is not found
            assert response.status_code == 404
            assert "Citizen not found" in response.json()["detail"]

            # Verify mock was called
            mock_get.assert_called_once_with("non-existent-id")

    def test_delete_citizen_profile_success(self, client, mock_citizen_data):
        with (
            patch(
                "routes.citizen.get_citizen", return_value=mock_citizen_data
            ) as mock_get,
            patch("routes.citizen.delete_citizen", return_value=True) as mock_delete,
        ):
            # Send delete request
            response = client.delete("/api/v1/citizens/test-citizen-id")

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Citizen profile deleted successfully"

            # Verify mocks were called
            mock_get.assert_called_once_with("test-citizen-id")
            mock_delete.assert_called_once_with("test-citizen-id")

    def test_get_wallet_success(self, client, mock_citizen_data):
        with patch(
            "routes.citizen.get_citizen", return_value=mock_citizen_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/citizens/test-citizen-id/wallet")

            # Verify response
            assert response.status_code == 200
            assert "govt_wallet" in response.json()
            assert "personal_wallet" in response.json()

            # Verify mock was called
            mock_get.assert_called_once_with("test-citizen-id")

    def test_generate_qr_success(self, client, mock_citizen_data):
        with patch(
            "routes.citizen.get_citizen", return_value=mock_citizen_data
        ) as mock_get:
            # Send request
            response = client.get("/api/v1/citizens/test-citizen-id/generate-qr")

            # Verify response
            assert response.status_code == 200
            assert "qr_code" in response.json()
            assert "user_id" in response.json()
            assert response.json()["user_id"] == "test-citizen-id"

            # Verify mock was called
            mock_get.assert_called_once_with("test-citizen-id")

    def test_get_transactions(self, client, mock_transaction_data):
        transaction_list = [mock_transaction_data]

        # Mock query functions to return transactions
        with patch("routes.citizen.query_transactions_by_field") as mock_query:
            # Configure mock to return different values based on arguments
            mock_query.side_effect = (
                lambda field, value: transaction_list
                if value == "test-citizen-id"
                else []
            )

            # Send request
            response = client.get("/api/v1/citizens/test-citizen-id/transactions")

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0

            # Verify mock was called twice (for from_id and to_id)
            assert mock_query.call_count == 2

    def test_pay_vendor_success(
        self, client, mock_citizen_data, mock_vendor_data, mock_transaction_data
    ):
        # Deep copy wallet balances to avoid test side effects
        mock_citizen_data_with_balance = mock_citizen_data.copy()
        mock_citizen_data_with_balance["wallet_info"] = {
            "govt_wallet": {"balance": 5000.0, "transactions": []},
            "personal_wallet": {"balance": 10000.0, "transactions": []},
        }

        # Mock functions
        with (
            patch(
                "routes.citizen.get_citizen",
                return_value=mock_citizen_data_with_balance,
            ) as mock_get_citizen,
            patch(
                "routes.citizen.get_vendor", return_value=mock_vendor_data
            ) as mock_get_vendor,
            patch("routes.citizen.Transaction") as mock_transaction_cls,
            patch(
                "routes.citizen.update_citizen", return_value=True
            ) as mock_update_citizen,
            patch(
                "routes.citizen.update_vendor", return_value=True
            ) as mock_update_vendor,
            patch("routes.citizen.array_union", return_value=True) as mock_array_union,
            patch(
                "routes.citizen.save_transaction", return_value=True
            ) as mock_save_transaction,
        ):
            # Configure transaction mock
            transaction_instance = MagicMock()
            transaction_instance.id = "test-transaction-id"
            transaction_instance.to_dict.return_value = mock_transaction_data
            mock_transaction_cls.return_value = transaction_instance

            # Send payment request
            payment_data = {
                "vendor_id": "test-vendor-id",
                "amount": 1000.0,
                "wallet_type": "personal_wallet",
                "description": "Test payment",
            }
            response = client.post(
                "/api/v1/citizens/test-citizen-id/pay", json=payment_data
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Payment successful"
            assert response.json()["transaction_id"] == "test-transaction-id"

            # Verify mocks were called
            mock_get_citizen.assert_called_once_with("test-citizen-id")
            mock_get_vendor.assert_called_once_with("test-vendor-id")
            mock_update_citizen.assert_called_once()
            mock_update_vendor.assert_called_once()
            assert mock_array_union.call_count == 2
            mock_save_transaction.assert_called_once_with(
                "test-transaction-id", mock_transaction_data
            )

    def test_pay_vendor_insufficient_balance(self, client, mock_citizen_data):
        # Set a low balance
        mock_citizen_data_with_low_balance = mock_citizen_data.copy()
        mock_citizen_data_with_low_balance["wallet_info"] = {
            "personal_wallet": {"balance": 500.0, "transactions": []},
            "govt_wallet": {"balance": 0.0, "transactions": []},
        }

        with patch(
            "routes.citizen.get_citizen",
            return_value=mock_citizen_data_with_low_balance,
        ) as mock_get_citizen:
            # Send payment request with amount higher than balance
            payment_data = {
                "vendor_id": "test-vendor-id",
                "amount": 1000.0,
                "wallet_type": "personal_wallet",
                "description": "Test payment",
            }
            response = client.post(
                "/api/v1/citizens/test-citizen-id/pay", json=payment_data
            )

            # Verify response is bad request
            assert response.status_code == 400
            assert "Insufficient balance" in response.json()["detail"]

            # Verify mock was called
            mock_get_citizen.assert_called_once_with("test-citizen-id")

    def test_get_eligible_schemes(self, client, mock_citizen_data, mock_scheme_data):
        with (
            patch(
                "routes.citizen.get_citizen", return_value=mock_citizen_data
            ) as mock_get_citizen,
            patch(
                "routes.citizen.get_all_schemes", return_value=[mock_scheme_data]
            ) as mock_get_schemes,
        ):
            # Send request
            response = client.get("/api/v1/citizens/test-citizen-id/eligible-schemes")

            # Verify response
            assert response.status_code == 200
            assert isinstance(response.json(), list)

            # If scheme is eligible, there should be at least one item
            if len(response.json()) > 0:
                scheme = response.json()[0]
                assert "id" in scheme
                assert "eligible" in scheme
                assert "eligibility_check" in scheme

            # Verify mocks were called
            mock_get_citizen.assert_called_once_with("test-citizen-id")
            mock_get_schemes.assert_called_once()
