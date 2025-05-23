import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class Transaction:
    def __init__(
        self,
        from_id: str,
        to_id: str,
        amount: float,
        tx_type: str,
        scheme_id: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.id = str(uuid.uuid4())
        self.from_id = from_id  # ID of the sender (govt, citizen, vendor)
        self.to_id = to_id  # ID of the recipient (citizen, vendor)
        self.amount = amount
        self.tx_type = tx_type  # govt_to_citizen, citizen_to_vendor, etc.
        self.scheme_id = scheme_id  # If it's a government disbursement
        self.description = description or "Transaction"
        self.status = "completed"  # pending, completed, failed
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "amount": self.amount,
            "tx_type": self.tx_type,
            "scheme_id": self.scheme_id,
            "description": self.description,
            "status": self.status,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        transaction = cls(
            from_id=data["from_id"],
            to_id=data["to_id"],
            amount=data["amount"],
            tx_type=data["tx_type"],
            scheme_id=data.get("scheme_id"),
            description=data.get("description"),
        )
        transaction.id = data["id"]
        transaction.status = data["status"]
        transaction.timestamp = data["timestamp"]

        return transaction
