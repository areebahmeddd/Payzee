from fastapi import status
from unittest.mock import patch, MagicMock


class TestGovernmentRoutes:
    @patch("routes.government.get_government")
    def test_get_government_profile(
        self, mock_get_government, client, sample_government_data
    ):
        # Setup mock
        mock_get_government.return_value = sample_government_data

        # Make request
        response = client.get("/api/v1/governments/test-govt-id")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["account_info"]["name"] == "Test Government"
        assert "password" not in response.json()["account_info"]

    @patch("routes.government.get_government")
    def test_get_government_not_found(self, mock_get_government, client):
        # Setup mock to return None (government not found)
        mock_get_government.return_value = None

        # Make request
        response = client.get("/api/v1/governments/nonexistent-id")

        # Check response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()

    @patch("routes.government.get_government")
    @patch("routes.government.update_government")
    def test_update_government_profile(
        self,
        mock_update_government,
        mock_get_government,
        client,
        sample_government_data,
    ):
        # Setup mock
        mock_get_government.return_value = sample_government_data
        mock_update_government.return_value = True

        # Update data
        update_data = {"name": "Updated Govt Name", "department": "Updated Department"}

        # Make request
        response = client.put("/api/v1/governments/test-govt-id", json=update_data)

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Profile updated successfully"

        # Verify update_government was called
        mock_update_government.assert_called_once()

    @patch("routes.government.get_government")
    def test_get_wallet(self, mock_get_government, client, sample_government_data):
        # Setup mock
        mock_get_government.return_value = sample_government_data

        # Make request
        response = client.get("/api/v1/governments/test-govt-id/wallet")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["balance"] == 10000

    @patch("routes.government.get_government")
    @patch("routes.government.SchemeCreate")
    @patch("routes.government.Scheme")
    @patch("routes.government.save_scheme")
    @patch("routes.government.array_union")
    def test_create_scheme(
        self,
        mock_array_union,
        mock_save_scheme,
        mock_scheme_class,
        mock_scheme_create,
        mock_get_government,
        client,
        sample_government_data,
    ):
        # Setup mocks
        mock_get_government.return_value = sample_government_data

        # Setup Scheme class mock
        scheme_instance = MagicMock()
        scheme_instance.id = "new-scheme-id"
        scheme_instance.to_dict.return_value = {
            "id": "new-scheme-id",
            "name": "Test Scheme",
        }
        mock_scheme_class.return_value = scheme_instance

        # Make request with scheme data
        scheme_data = {
            "name": "Test Scheme",
            "description": "A test scheme description",
            "amount": 5000,
            "eligibility_criteria": {"age": {"min": 18}},
            "tags": ["test", "sample"],
        }

        response = client.post(
            "/api/v1/governments/test-govt-id/schemes", json=scheme_data
        )

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Scheme created successfully"
        assert response.json()["scheme_id"] == "new-scheme-id"

        # Verify functions were called
        mock_save_scheme.assert_called_once()
        mock_array_union.assert_called_once()

    @patch("routes.government.get_government")
    @patch("routes.government.get_scheme")
    @patch("routes.government.get_citizen")
    @patch("routes.government.update_citizen")
    @patch("routes.government.update_government")
    @patch("routes.government.save_transaction")
    @patch("routes.government.array_union")
    @patch("routes.government.Transaction")
    def test_disburse_funds(
        self,
        mock_transaction,
        mock_array_union,
        mock_save_transaction,
        mock_update_government,
        mock_update_citizen,
        mock_get_citizen,
        mock_get_scheme,
        mock_get_government,
        client,
        sample_government_data,
        sample_scheme_data,
        sample_citizen_data,
    ):
        # Setup mocks
        mock_get_government.return_value = sample_government_data

        # Setup scheme with beneficiaries
        scheme_with_beneficiaries = sample_scheme_data.copy()
        scheme_with_beneficiaries["beneficiaries"] = ["test-citizen-id"]
        mock_get_scheme.return_value = scheme_with_beneficiaries

        # Setup citizen
        mock_get_citizen.return_value = sample_citizen_data

        # Setup Transaction class mock
        transaction_instance = MagicMock()
        transaction_instance.id = "new-transaction-id"
        transaction_instance.to_dict.return_value = {
            "id": "new-transaction-id",
            "from_id": "test-govt-id",
            "to_id": "test-citizen-id",
            "amount": 500,
        }
        mock_transaction.return_value = transaction_instance

        # Make request
        disbursement_data = {"scheme_id": "test-scheme-id", "amount_per_user": 500}

        response = client.post(
            "/api/v1/governments/test-govt-id/disburse", json=disbursement_data
        )

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Funds disbursed successfully"
        assert response.json()["beneficiaries_count"] == 1

        # Verify functions were called
        mock_update_citizen.assert_called_once()
        mock_update_government.assert_called_once()
        mock_save_transaction.assert_called_once()
        assert mock_array_union.call_count == 2  # For citizen and government

    @patch("routes.government.get_government")
    @patch("routes.government.query_schemes_by_field")
    def test_get_schemes(
        self,
        mock_query_schemes,
        mock_get_government,
        client,
        sample_government_data,
        sample_scheme_data,
    ):
        # Setup mocks
        mock_get_government.return_value = sample_government_data
        mock_query_schemes.return_value = [sample_scheme_data]

        # Make request
        response = client.get("/api/v1/governments/test-govt-id/schemes")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == "test-scheme-id"

    @patch("routes.government.get_government")
    @patch("routes.government.get_all_citizens")
    def test_get_all_citizens(
        self,
        mock_get_all_citizens,
        mock_get_government,
        client,
        sample_government_data,
        sample_citizen_data,
    ):
        # Setup mocks
        mock_get_government.return_value = sample_government_data

        # Add password to test it gets removed
        citizen_with_password = sample_citizen_data.copy()
        citizen_with_password["account_info"]["password"] = "secret"
        mock_get_all_citizens.return_value = [citizen_with_password]

        # Make request
        response = client.get("/api/v1/governments/test-govt-id/all-citizens")

        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["account_info"]["id"] == "test-citizen-id"
        assert "password" not in response.json()[0]["account_info"]
