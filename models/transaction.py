import uuid
from datetime import datetime, timezone


class Transaction:
    def __init__(
        self, from_id, to_id, amount, transaction_type, scheme_id=None, description=None
    ):
        self.id = str(uuid.uuid4())
        self.from_id = from_id  # User ID of sender
        self.to_id = to_id  # User ID of receiver
        self.amount = amount
        self.transaction_type = (
            transaction_type  # govt-to-citizen, citizen-to-vendor, etc.
        )
        self.scheme_id = (
            scheme_id  # Optional reference to scheme if this is a scheme disbursement
        )
        self.description = description
        self.timestamp = datetime.now(timezone.utc)
        self.status = "completed"  # completed, pending, failed

    def to_dict(self):
        return {
            "id": self.id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "scheme_id": self.scheme_id,
            "description": self.description,
            "timestamp": self.timestamp,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        transaction = cls(
            from_id=data["from_id"],
            to_id=data["to_id"],
            amount=data["amount"],
            transaction_type=data["transaction_type"],
            scheme_id=data.get("scheme_id"),
            description=data.get("description"),
        )
        transaction.id = data["id"]
        transaction.timestamp = data["timestamp"]
        transaction.status = data["status"]
        return transaction
