from datetime import date, datetime
from uuid import UUID

# Sample Users
users_data = [
    {
        "aadhaar_number": "123456789012",
        "name": "Rahul Sharma",
        "date_of_birth": date(1990, 5, 15),
        "gender": "Male",
        "state": "Karnataka",
        "district": "Bangalore",
        "phone_number": "9876543210",
        "email": "rahul.sharma@example.com",
        "caste_category": "General",
        "income_group": "Middle",
        "tags": ["Student", "Tech"]
    },
    {
        "aadhaar_number": "234567890123",
        "name": "Priya Patel",
        "date_of_birth": date(1995, 8, 20),
        "gender": "Female",
        "state": "Maharashtra",
        "district": "Mumbai",
        "phone_number": "8765432109",
        "email": "priya.patel@example.com",
        "caste_category": "OBC",
        "income_group": "Low",
        "tags": ["Farmer", "Rural"]
    },
    {
        "aadhaar_number": "345678901234",
        "name": "Amit Kumar",
        "date_of_birth": date(1988, 3, 10),
        "gender": "Male",
        "state": "Delhi",
        "district": "New Delhi",
        "phone_number": "7654321098",
        "email": "amit.kumar@example.com",
        "caste_category": "SC",
        "income_group": "High",
        "tags": ["Business", "Urban"]
    }
]

# Sample Vendors
vendors_data = [
    {
        "name": "Tech Solutions Ltd",
        "aadhaar_number": "456789012345",
        "gst_number": "GST123456789",
        "phone_number": "9876543211",
        "state": "Karnataka",
        "district": "Bangalore",
        "services_offered": ["Electronics", "Computers", "Accessories"],
        "kyc_status": "Verified"
    },
    {
        "name": "Rural Supplies Co",
        "aadhaar_number": "567890123456",
        "gst_number": "GST234567890",
        "phone_number": "8765432108",
        "state": "Maharashtra",
        "district": "Pune",
        "services_offered": ["Agricultural Equipment", "Fertilizers", "Seeds"],
        "kyc_status": "Verified"
    },
    {
        "name": "Education Store",
        "aadhaar_number": "678901234567",
        "gst_number": "GST345678901",
        "phone_number": "7654321097",
        "state": "Delhi",
        "district": "New Delhi",
        "services_offered": ["Books", "Stationery", "Educational Kits"],
        "kyc_status": "Pending"
    }
]

# Sample Schemes
schemes_data = [
    {
        "name": "PM Stationery Yojana 2024",
        "description": "Free stationery for students from economically weaker sections",
        "amount_per_user": 1000.00,
        "eligibility_criteria": {
            "income_group": ["Low"],
            "tags": ["Student"],
            "states": ["Karnataka", "Maharashtra", "Delhi"]
        }
    },
    {
        "name": "Farmer Support Scheme",
        "description": "Financial assistance for farmers to purchase agricultural equipment",
        "amount_per_user": 5000.00,
        "eligibility_criteria": {
            "tags": ["Farmer"],
            "states": ["Karnataka", "Maharashtra"],
            "income_group": ["Low", "Middle"]
        }
    },
    {
        "name": "Digital Literacy Program",
        "description": "Support for purchasing computers and digital devices",
        "amount_per_user": 15000.00,
        "eligibility_criteria": {
            "tags": ["Student"],
            "states": ["Karnataka", "Delhi"],
            "income_group": ["Low", "Middle"]
        }
    }
]

# Sample Transactions
transactions_data = [
    {
        "user_id": None,  # Will be set during seeding
        "vendor_id": None,  # Will be set during seeding
        "scheme_id": None,  # Will be set during seeding
        "amount": 1000.00,
        "status": "Completed",
        "used_for": "Stationery items"
    },
    {
        "user_id": None,  # Will be set during seeding
        "vendor_id": None,  # Will be set during seeding
        "scheme_id": None,  # Will be set during seeding
        "amount": 5000.00,
        "status": "Pending",
        "used_for": "Agricultural equipment"
    },
    {
        "user_id": None,  # Will be set during seeding
        "vendor_id": None,  # Will be set during seeding
        "scheme_id": None,  # Will be set during seeding
        "amount": 15000.00,
        "status": "Completed",
        "used_for": "Laptop purchase"
    }
] 