from typing import Any, Dict, List, Optional
from db.redis_operations import (
    get_document,
    set_document,
    update_document,
    delete_document,
    query_by_field,
    get_all_documents,
    array_union,
)
from db.redis_config import (
    CITIZENS_PREFIX,
    CITIZENS_SET,
    VENDORS_PREFIX,
    VENDORS_SET,
    GOVERNMENTS_PREFIX,
    GOVERNMENTS_SET,
    SCHEMES_PREFIX,
    SCHEMES_SET,
    TRANSACTIONS_PREFIX,
    TRANSACTIONS_SET,
)


# Citizen operations
def get_citizen(citizen_id: str) -> Optional[Dict[str, Any]]:
    """Get a citizen by ID"""
    return get_document(CITIZENS_PREFIX, citizen_id)


def save_citizen(citizen_id: str, data: Dict[str, Any]) -> str:
    """Save a citizen document"""
    return set_document(CITIZENS_PREFIX, citizen_id, data, CITIZENS_SET)


def update_citizen(citizen_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a citizen document"""
    return update_document(CITIZENS_PREFIX, citizen_id, update_data)


def delete_citizen(citizen_id: str) -> bool:
    """Delete a citizen document"""
    return delete_document(CITIZENS_PREFIX, citizen_id, CITIZENS_SET)


def query_citizens_by_field(field: str, value: Any) -> List[Dict[str, Any]]:
    """Query citizens by a field value"""
    return query_by_field(CITIZENS_PREFIX, CITIZENS_SET, field, value)


def get_all_citizens() -> List[Dict[str, Any]]:
    """Get all citizens"""
    return get_all_documents(CITIZENS_PREFIX, CITIZENS_SET)


# Vendor operations
def get_vendor(vendor_id: str) -> Optional[Dict[str, Any]]:
    """Get a vendor by ID"""
    return get_document(VENDORS_PREFIX, vendor_id)


def save_vendor(vendor_id: str, data: Dict[str, Any]) -> str:
    """Save a vendor document"""
    return set_document(VENDORS_PREFIX, vendor_id, data, VENDORS_SET)


def update_vendor(vendor_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a vendor document"""
    return update_document(VENDORS_PREFIX, vendor_id, update_data)


def delete_vendor(vendor_id: str) -> bool:
    """Delete a vendor document"""
    return delete_document(VENDORS_PREFIX, vendor_id, VENDORS_SET)


def query_vendors_by_field(field: str, value: Any) -> List[Dict[str, Any]]:
    """Query vendors by a field value"""
    return query_by_field(VENDORS_PREFIX, VENDORS_SET, field, value)


def get_all_vendors() -> List[Dict[str, Any]]:
    """Get all vendors"""
    return get_all_documents(VENDORS_PREFIX, VENDORS_SET)


# Government operations
def get_government(govt_id: str) -> Optional[Dict[str, Any]]:
    """Get a government by ID"""
    return get_document(GOVERNMENTS_PREFIX, govt_id)


def save_government(govt_id: str, data: Dict[str, Any]) -> str:
    """Save a government document"""
    return set_document(GOVERNMENTS_PREFIX, govt_id, data, GOVERNMENTS_SET)


def update_government(govt_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a government document"""
    return update_document(GOVERNMENTS_PREFIX, govt_id, update_data)


def delete_government(govt_id: str) -> bool:
    """Delete a government document"""
    return delete_document(GOVERNMENTS_PREFIX, govt_id, GOVERNMENTS_SET)


def query_governments_by_field(field: str, value: Any) -> List[Dict[str, Any]]:
    """Query governments by a field value"""
    return query_by_field(GOVERNMENTS_PREFIX, GOVERNMENTS_SET, field, value)


def get_all_governments() -> List[Dict[str, Any]]:
    """Get all governments"""
    return get_all_documents(GOVERNMENTS_PREFIX, GOVERNMENTS_SET)


# Scheme operations
def get_scheme(scheme_id: str) -> Optional[Dict[str, Any]]:
    """Get a scheme by ID"""
    return get_document(SCHEMES_PREFIX, scheme_id)


def save_scheme(scheme_id: str, data: Dict[str, Any]) -> str:
    """Save a scheme document"""
    return set_document(SCHEMES_PREFIX, scheme_id, data, SCHEMES_SET)


def update_scheme(scheme_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a scheme document"""
    return update_document(SCHEMES_PREFIX, scheme_id, update_data)


def query_schemes_by_field(field: str, value: Any) -> List[Dict[str, Any]]:
    """Query schemes by a field value"""
    return query_by_field(SCHEMES_PREFIX, SCHEMES_SET, field, value)


def get_all_schemes() -> List[Dict[str, Any]]:
    """Get all schemes"""
    return get_all_documents(SCHEMES_PREFIX, SCHEMES_SET)


def add_beneficiary_to_scheme(scheme_id: str, citizen_id: str) -> bool:
    """Add a citizen beneficiary to a scheme"""
    return array_union(SCHEMES_PREFIX, scheme_id, "beneficiaries", [citizen_id])


# Transaction operations
def get_transaction(transaction_id: str) -> Optional[Dict[str, Any]]:
    """Get a transaction by ID"""
    return get_document(TRANSACTIONS_PREFIX, transaction_id)


def save_transaction(transaction_id: str, data: Dict[str, Any]) -> str:
    """Save a transaction document"""
    return set_document(TRANSACTIONS_PREFIX, transaction_id, data, TRANSACTIONS_SET)


def update_transaction(transaction_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a transaction document"""
    return update_document(TRANSACTIONS_PREFIX, transaction_id, update_data)


def query_transactions_by_field(field: str, value: Any) -> List[Dict[str, Any]]:
    """Query transactions by a field value"""
    return query_by_field(TRANSACTIONS_PREFIX, TRANSACTIONS_SET, field, value)


def get_all_transactions() -> List[Dict[str, Any]]:
    """Get all transactions"""
    return get_all_documents(TRANSACTIONS_PREFIX, TRANSACTIONS_SET)
