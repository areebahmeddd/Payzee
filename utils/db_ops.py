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
def get_citizen(citizen_id):
    """Get a citizen by ID"""
    return get_document(CITIZENS_PREFIX, citizen_id)


def save_citizen(citizen_id, data):
    """Save a citizen document"""
    return set_document(CITIZENS_PREFIX, citizen_id, data, CITIZENS_SET)


def update_citizen(citizen_id, update_data):
    """Update a citizen document"""
    return update_document(CITIZENS_PREFIX, citizen_id, update_data)


def delete_citizen(citizen_id):
    """Delete a citizen document"""
    return delete_document(CITIZENS_PREFIX, citizen_id, CITIZENS_SET)


def query_citizens_by_field(field, value):
    """Query citizens by a field value"""
    return query_by_field(CITIZENS_PREFIX, CITIZENS_SET, field, value)


def get_all_citizens():
    """Get all citizens"""
    return get_all_documents(CITIZENS_PREFIX, CITIZENS_SET)


# Vendor operations
def get_vendor(vendor_id):
    """Get a vendor by ID"""
    return get_document(VENDORS_PREFIX, vendor_id)


def save_vendor(vendor_id, data):
    """Save a vendor document"""
    return set_document(VENDORS_PREFIX, vendor_id, data, VENDORS_SET)


def update_vendor(vendor_id, update_data):
    """Update a vendor document"""
    return update_document(VENDORS_PREFIX, vendor_id, update_data)


def delete_vendor(vendor_id):
    """Delete a vendor document"""
    return delete_document(VENDORS_PREFIX, vendor_id, VENDORS_SET)


def query_vendors_by_field(field, value):
    """Query vendors by a field value"""
    return query_by_field(VENDORS_PREFIX, VENDORS_SET, field, value)


def get_all_vendors():
    """Get all vendors"""
    return get_all_documents(VENDORS_PREFIX, VENDORS_SET)


# Government operations
def get_government(govt_id):
    """Get a government by ID"""
    return get_document(GOVERNMENTS_PREFIX, govt_id)


def save_government(govt_id, data):
    """Save a government document"""
    return set_document(GOVERNMENTS_PREFIX, govt_id, data, GOVERNMENTS_SET)


def update_government(govt_id, update_data):
    """Update a government document"""
    return update_document(GOVERNMENTS_PREFIX, govt_id, update_data)


def delete_government(govt_id):
    """Delete a government document"""
    return delete_document(GOVERNMENTS_PREFIX, govt_id, GOVERNMENTS_SET)


def query_governments_by_field(field, value):
    """Query governments by a field value"""
    return query_by_field(GOVERNMENTS_PREFIX, GOVERNMENTS_SET, field, value)


def get_all_governments():
    """Get all governments"""
    return get_all_documents(GOVERNMENTS_PREFIX, GOVERNMENTS_SET)


# Scheme operations
def get_scheme(scheme_id):
    """Get a scheme by ID"""
    return get_document(SCHEMES_PREFIX, scheme_id)


def save_scheme(scheme_id, data):
    """Save a scheme document"""
    return set_document(SCHEMES_PREFIX, scheme_id, data, SCHEMES_SET)


def update_scheme(scheme_id, update_data):
    """Update a scheme document"""
    return update_document(SCHEMES_PREFIX, scheme_id, update_data)


def query_schemes_by_field(field, value):
    """Query schemes by a field value"""
    return query_by_field(SCHEMES_PREFIX, SCHEMES_SET, field, value)


def get_all_schemes():
    """Get all schemes"""
    return get_all_documents(SCHEMES_PREFIX, SCHEMES_SET)


def add_beneficiary_to_scheme(scheme_id, citizen_id):
    """Add a citizen beneficiary to a scheme"""
    return array_union(SCHEMES_PREFIX, scheme_id, "beneficiaries", [citizen_id])


# Transaction operations
def get_transaction(transaction_id):
    """Get a transaction by ID"""
    return get_document(TRANSACTIONS_PREFIX, transaction_id)


def save_transaction(transaction_id, data):
    """Save a transaction document"""
    return set_document(TRANSACTIONS_PREFIX, transaction_id, data, TRANSACTIONS_SET)


def update_transaction(transaction_id, update_data):
    """Update a transaction document"""
    return update_document(TRANSACTIONS_PREFIX, transaction_id, update_data)


def query_transactions_by_field(field, value):
    """Query transactions by a field value"""
    return query_by_field(TRANSACTIONS_PREFIX, TRANSACTIONS_SET, field, value)


def get_all_transactions():
    """Get all transactions"""
    return get_all_documents(TRANSACTIONS_PREFIX, TRANSACTIONS_SET)
