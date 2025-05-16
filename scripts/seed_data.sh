#!/bin/bash

echo "Seeding test data into Redis..."
echo "==============================="

PYTHON_SCRIPT=$(cat << 'EOF'
import os
import json
import uuid
import random
import redis
from datetime import datetime, timedelta

CITIZENS_PREFIX = "citizen:"
CITIZENS_SET = "citizens"
VENDORS_PREFIX = "vendor:"
VENDORS_SET = "vendors"
GOVERNMENTS_PREFIX = "govt:"
GOVERNMENTS_SET = "governments"
SCHEMES_PREFIX = "scheme:"
SCHEMES_SET = "schemes"
TRANSACTIONS_PREFIX = "txn:"
TRANSACTIONS_SET = "transactions"

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_db = int(os.environ.get("REDIS_DB", 0))

redis_client = redis.Redis(
    host=redis_host, port=redis_port, db=redis_db, decode_responses=True
)
redis_client.ping()
print(f"Connected to Redis at {redis_host}:{redis_port}")


def serialize_for_db(data):
    return json.dumps(data)


def deserialize_from_db(data):
    return json.loads(data)


print("Clearing Redis database...")
redis_client.flushall()
redis_client.ping()
print("Database cleared.\n")

print("Creating citizens...")
citizens = [
    {
        "name": "Areeb Ahmed",
        "email": "areeb@example.com",
        "password": "citizen@123",
        "phone": "+91 9876543210",
        "address": "42, Linking Road, Bandra West, Mumbai, Maharashtra, 400050",
        "id_type": "Aadhaar",
        "id_number": "123456789012",
        "gender": "male",
        "occupation": "software engineer",
        "caste": "General",
        "dob": "1990-05-15",
        "annual_income": 1400000,
        "image_url": "https://cdn.pixabay.com/photo/2023/11/17/21/43/trail-8395089_1280.jpg",
    },
    {
        "name": "Shivansh Karan",
        "email": "shivansh@example.com",
        "password": "citizen@123",
        "phone": "+91 8765432109",
        "address": "15, MG Road, Satara, Maharashtra, 415001",
        "id_type": "Aadhaar",
        "id_number": "234567890123",
        "gender": "male",
        "occupation": "farmer",
        "caste": "OBC",
        "dob": "1985-08-22",
        "annual_income": 80000,
        "image_url": "https://cdn.pixabay.com/photo/2019/10/02/17/19/mountains-4521455_1280.jpg",
    },
    {
        "name": "Alfiya Fatima",
        "email": "alfiya@example.com",
        "password": "citizen@123",
        "phone": "+91 7654321098",
        "address": "78, Civil Lines, Delhi, 110054",
        "id_type": "Aadhaar",
        "id_number": "345678901234",
        "gender": "female",
        "occupation": "student",
        "caste": "SC",
        "dob": "1998-12-10",
        "annual_income": 150000,
        "image_url": "https://cdn.pixabay.com/photo/2022/05/14/15/49/mountain-7195958_1280.jpg",
    },
]

citizen_ids = []
for citizen_data in citizens:
    citizen_id = str(uuid.uuid4())
    citizen_ids.append(citizen_id)

    citizen = {
        "account_info": {
            "id": citizen_id,
            "name": citizen_data["name"],
            "email": citizen_data["email"],
            "password": citizen_data["password"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_type": "citizen",
            "image_url": citizen_data["image_url"],
        },
        "personal_info": {
            "phone": citizen_data["phone"],
            "id_type": citizen_data["id_type"],
            "id_number": citizen_data["id_number"],
            "address": citizen_data["address"],
            "dob": citizen_data["dob"],
            "gender": citizen_data["gender"],
            "occupation": citizen_data["occupation"],
            "caste": citizen_data["caste"],
            "annual_income": citizen_data["annual_income"],
        },
        "wallet_info": {
            "govt_wallet": {"balance": random.randint(500, 5000), "transactions": []},
            "personal_wallet": {
                "balance": random.randint(5000, 10000),
                "transactions": [],
            },
        },
        "scheme_info": [],
    }

    redis_client.set(f"{CITIZENS_PREFIX}{citizen_id}", serialize_for_db(citizen))
    redis_client.sadd(CITIZENS_SET, citizen_id)

    print(f"Added citizen: {citizen_data['name']}")

print("\nCreating vendors...")
vendors = [
    {
        "name": "Rajan Malhotra",
        "email": "rajan@example.com",
        "password": "vendor@123",
        "gender": "male",
        "business_name": "Malhotra Grocery Mart",
        "business_id": "GSTIN22AAAAA1111Z",
        "license_type": "private",
        "phone": "+91 9988776655",
        "address": "23, Krishna Market, Lajpat Nagar, New Delhi, 110024",
        "occupation": "retail business",
        "image_url": "https://cdn.pixabay.com/photo/2019/07/20/20/11/nature-4351455_1280.jpg",
    },
    {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "password": "vendor@123",
        "gender": "female",
        "business_name": "MedPlus Pharmacy",
        "business_id": "GSTIN09BBBBB2222Y",
        "license_type": "public",
        "phone": "+91 8877665544",
        "address": "56, Sector 18, Noida, Uttar Pradesh, 201301",
        "occupation": "healthcare",
        "image_url": "https://cdn.pixabay.com/photo/2019/10/07/11/26/winter-landscape-4532412_1280.jpg",
    },
    {
        "name": "Abdul Khan",
        "email": "abdul@example.com",
        "password": "vendor@123",
        "gender": "male",
        "business_name": "Khan Kirana Store",
        "business_id": "GSTIN19CCCCC3333X",
        "license_type": "government",
        "phone": "+91 7766554433",
        "address": "10, Park Street, Kolkata, West Bengal, 700016",
        "occupation": "retail business",
        "image_url": "https://cdn.pixabay.com/photo/2024/09/03/18/03/sand-9019849_1280.jpg",
    },
]

vendor_ids = []
for vendor_data in vendors:
    vendor_id = str(uuid.uuid4())
    vendor_ids.append(vendor_id)

    vendor = {
        "account_info": {
            "id": vendor_id,
            "name": vendor_data["name"],
            "email": vendor_data["email"],
            "gender": vendor_data["gender"],
            "password": vendor_data["password"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_type": "vendor",
            "image_url": vendor_data["image_url"],
        },
        "business_info": {
            "business_name": vendor_data["business_name"],
            "business_id": vendor_data["business_id"],
            "license_type": vendor_data["license_type"],
            "phone": vendor_data["phone"],
            "address": vendor_data["address"],
            "occupation": vendor_data["occupation"],
        },
        "wallet_info": {"balance": random.randint(5000, 20000), "transactions": []},
    }

    redis_client.set(f"{VENDORS_PREFIX}{vendor_id}", serialize_for_db(vendor))
    redis_client.sadd(VENDORS_SET, vendor_id)

    print(f"Added vendor: {vendor_data['business_name']}")

print("\nCreating government entities...")
governments = [
    {
        "name": "Ministry of Social Justice",
        "email": "social.justice@gov.in",
        "password": "govt@123",
        "jurisdiction": "Central",
        "govt_id": "DOPT0001",
        "image_url": "https://cdn.pixabay.com/photo/2016/10/24/22/43/dubai-1767540_1280.jpg",
    },
    {
        "name": "Karnataka Rural Development",
        "email": "rural.dev@karnataka.gov.in",
        "password": "govt@123",
        "jurisdiction": "State",
        "govt_id": "KARD0002",
        "image_url": "https://cdn.pixabay.com/photo/2023/06/21/16/26/warnemunde-8079731_1280.jpg",
    },
    {
        "name": "Delhi Social Welfare Department",
        "email": "dsw@delhi.gov.in",
        "password": "govt@123",
        "jurisdiction": "State",
        "govt_id": "DELSW003",
        "image_url": "https://cdn.pixabay.com/photo/2024/02/23/21/25/landscape-8592826_1280.jpg",
    },
]

govt_ids = []
for govt_data in governments:
    govt_id = str(uuid.uuid4())
    govt_ids.append(govt_id)

    govt = {
        "account_info": {
            "id": govt_id,
            "name": govt_data["name"],
            "email": govt_data["email"],
            "password": govt_data["password"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_type": "government",
            "jurisdiction": govt_data["jurisdiction"],
            "govt_id": govt_data["govt_id"],
            "image_url": govt_data["image_url"],
        },
        "wallet_info": {
            "balance": random.randint(1000000, 10000000),
            "schemes": [],
            "transactions": [],
        },
    }

    redis_client.set(f"{GOVERNMENTS_PREFIX}{govt_id}", serialize_for_db(govt))
    redis_client.sadd(GOVERNMENTS_SET, govt_id)

    print(f"Added government entity: {govt_data['name']}")

print("\nCreating schemes...")
schemes = [
    {
        "name": "PM Kisan Samman Nidhi",
        "description": "Direct income support of ₹6,000 per year to eligible farmer families",
        "govt_id": govt_ids[0],
        "amount": 6000,
        "status": "active",
        "eligibility_criteria": {
            "occupation": "farmer",
            "min_age": 18,
            "max_age": 65,
            "gender": "any",
            "state": "Maharashtra",
            "district": "all",
            "city": "all",
            "caste": "OBC",
            "annual_income": 100000,
        },
        "tags": ["agriculture", "farmer-welfare", "income-support"],
    },
    {
        "name": "Vidyarthi Shiksha Yojana",
        "description": "Scholarship for higher education students from rural Karnataka",
        "govt_id": govt_ids[1],
        "amount": 15000,
        "status": "active",
        "eligibility_criteria": {
            "occupation": "student",
            "min_age": 17,
            "max_age": 25,
            "gender": "any",
            "state": "Karnataka",
            "district": "Bangalore Rural",
            "city": "Doddaballapur",
            "caste": "SC",
            "annual_income": 300000,
        },
        "tags": ["education", "scholarship", "rural"],
    },
    {
        "name": "Delhi Swasthya Bima Yojana",
        "description": "Health insurance coverage for Delhi residents below poverty line",
        "govt_id": govt_ids[2],
        "amount": 5000,
        "status": "active",
        "eligibility_criteria": {
            "occupation": "any",
            "min_age": 0,
            "max_age": 100,
            "gender": "any",
            "state": "Delhi",
            "district": "all",
            "city": "all",
            "caste": "all",
            "annual_income": 250000,
        },
        "tags": ["health", "insurance", "poverty"],
    },
    {
        "name": "Maharashtra Women Farmer Support",
        "description": "Special support scheme for women farmers in Maharashtra",
        "govt_id": govt_ids[0],
        "amount": 10000,
        "status": "active",
        "eligibility_criteria": {
            "occupation": "farmer",
            "min_age": 18,
            "max_age": 65,
            "gender": "female",
            "state": "Maharashtra",
            "district": "all",
            "city": "all",
            "caste": "all",
            "annual_income": 150000,
        },
        "tags": ["agriculture", "women-empowerment", "rural-development"],
    },
    {
        "name": "Tech Talent Scholarship",
        "description": "Financial aid for software engineers and tech professionals",
        "govt_id": govt_ids[1],
        "amount": 25000,
        "status": "active",
        "eligibility_criteria": {
            "occupation": "software engineer",
            "min_age": 21,
            "max_age": 40,
            "gender": "any",
            "state": "all",
            "district": "all",
            "city": "all",
            "caste": "General",
            "annual_income": 1500000,
        },
        "tags": ["technology", "education", "career-development"],
    },
]

scheme_ids = []
for scheme_data in schemes:
    scheme_id = str(uuid.uuid4())
    scheme_ids.append(scheme_id)

    eligible_beneficiaries = []

    for cid in citizen_ids:
        citizen = deserialize_from_db(redis_client.get(f"{CITIZENS_PREFIX}{cid}"))
        personal_info = citizen["personal_info"]

        eligible = True

        if (
            scheme_data["eligibility_criteria"]["occupation"] != "any"
            and scheme_data["eligibility_criteria"]["occupation"]
            != personal_info["occupation"]
        ):
            eligible = False

        if (
            scheme_data["eligibility_criteria"]["gender"] != "any"
            and scheme_data["eligibility_criteria"]["gender"] != personal_info["gender"]
        ):
            eligible = False

        if (
            scheme_data["eligibility_criteria"]["caste"] != "all"
            and scheme_data["eligibility_criteria"]["caste"] != personal_info["caste"]
        ):
            eligible = False

        if (
            personal_info["annual_income"]
            > scheme_data["eligibility_criteria"]["annual_income"]
        ):
            eligible = False

        dob_str = personal_info["dob"]
        year, month, day = map(int, dob_str.split("-"))
        dob = datetime(year, month, day)
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if (
            age < scheme_data["eligibility_criteria"]["min_age"]
            or age > scheme_data["eligibility_criteria"]["max_age"]
        ):
            eligible = False

        if (
            scheme_data["eligibility_criteria"]["state"] != "all"
            and scheme_data["eligibility_criteria"]["state"]
            not in personal_info["address"]
        ):
            eligible = False

        if eligible:
            eligible_beneficiaries.append(cid)

            if "scheme_info" not in citizen:
                citizen["scheme_info"] = []
            citizen["scheme_info"].append(scheme_id)
            redis_client.set(f"{CITIZENS_PREFIX}{cid}", serialize_for_db(citizen))

    scheme = {
        "id": scheme_id,
        "name": scheme_data["name"],
        "description": scheme_data["description"],
        "govt_id": scheme_data["govt_id"],
        "amount": scheme_data["amount"],
        "status": scheme_data["status"],
        "eligibility_criteria": scheme_data["eligibility_criteria"],
        "tags": scheme_data["tags"],
        "beneficiaries": eligible_beneficiaries,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    redis_client.set(f"{SCHEMES_PREFIX}{scheme_id}", serialize_for_db(scheme))
    redis_client.sadd(SCHEMES_SET, scheme_id)

    govt_key = f"{GOVERNMENTS_PREFIX}{scheme_data['govt_id']}"
    govt_data = redis_client.get(govt_key)
    if govt_data:
        govt_dict = deserialize_from_db(govt_data)
        govt_dict["wallet_info"]["schemes"].append(scheme_id)
        redis_client.set(govt_key, serialize_for_db(govt_dict))

    print(
        f"Added scheme: {scheme_data['name']} with {len(eligible_beneficiaries)} beneficiaries"
    )

print("\nCreating transactions...")
transactions = []
transaction_count = 0

for scheme_id in scheme_ids:
    scheme_data = redis_client.get(f"{SCHEMES_PREFIX}{scheme_id}")
    scheme = deserialize_from_db(scheme_data)

    govt_data = redis_client.get(f"{GOVERNMENTS_PREFIX}{scheme['govt_id']}")
    govt = deserialize_from_db(govt_data)

    beneficiaries = scheme["beneficiaries"]
    if not beneficiaries:
        beneficiaries = random.sample(citizen_ids, min(1, len(citizen_ids)))

    for citizen_id in beneficiaries:
        txn_id = str(uuid.uuid4())
        citizen_data = redis_client.get(f"{CITIZENS_PREFIX}{citizen_id}")
        citizen = deserialize_from_db(citizen_data)

        transaction = {
            "id": txn_id,
            "from_id": scheme["govt_id"],
            "to_id": citizen_id,
            "amount": scheme["amount"],
            "tx_type": "government-to-citizen",
            "scheme_id": scheme["id"],
            "description": f"Disbursement for {scheme['name']}",
            "timestamp": (
                datetime.now() - timedelta(days=random.randint(5, 30))
            ).isoformat(),
            "status": "completed",
        }

        redis_client.set(
            f"{TRANSACTIONS_PREFIX}{txn_id}", serialize_for_db(transaction)
        )
        redis_client.sadd(TRANSACTIONS_SET, txn_id)

        citizen["wallet_info"]["govt_wallet"]["balance"] += scheme["amount"]
        if "transactions" not in citizen["wallet_info"]["govt_wallet"]:
            citizen["wallet_info"]["govt_wallet"]["transactions"] = []

        citizen["wallet_info"]["govt_wallet"]["transactions"].append(txn_id)
        redis_client.set(f"{CITIZENS_PREFIX}{citizen_id}", serialize_for_db(citizen))

        govt["wallet_info"]["balance"] -= scheme["amount"]
        if "transactions" not in govt["wallet_info"]:
            govt["wallet_info"]["transactions"] = []

        govt["wallet_info"]["transactions"].append(txn_id)
        redis_client.set(
            f"{GOVERNMENTS_PREFIX}{scheme['govt_id']}", serialize_for_db(govt)
        )

        print(
            f"Created disbursement: {govt['account_info']['name']} to {citizen['account_info']['name']} (₹{scheme['amount']})"
        )
        transaction_count += 1

for i in range(len(citizen_ids)):
    for _ in range(2):
        txn_id = str(uuid.uuid4())
        vendor_id = random.choice(vendor_ids)

        citizen_data = redis_client.get(f"{CITIZENS_PREFIX}{citizen_ids[i]}")
        citizen = deserialize_from_db(citizen_data)

        vendor_data = redis_client.get(f"{VENDORS_PREFIX}{vendor_id}")
        vendor = deserialize_from_db(vendor_data)

        amount = min(
            random.randint(100, 1000),
            citizen["wallet_info"]["personal_wallet"]["balance"],
        )
        if amount <= 0:
            citizen["wallet_info"]["personal_wallet"]["balance"] = 1000
            amount = 500

        transaction = {
            "id": txn_id,
            "from_id": citizen_ids[i],
            "to_id": vendor_id,
            "amount": amount,
            "tx_type": "citizen-to-vendor",
            "scheme_id": None,
            "description": f"Purchase at {vendor['business_info']['business_name']}",
            "timestamp": (
                datetime.now() - timedelta(days=random.randint(1, 30))
            ).isoformat(),
            "status": "completed",
        }

        redis_client.set(
            f"{TRANSACTIONS_PREFIX}{txn_id}", serialize_for_db(transaction)
        )
        redis_client.sadd(TRANSACTIONS_SET, txn_id)

        citizen["wallet_info"]["personal_wallet"]["balance"] -= amount
        if "transactions" not in citizen["wallet_info"]["personal_wallet"]:
            citizen["wallet_info"]["personal_wallet"]["transactions"] = []

        citizen["wallet_info"]["personal_wallet"]["transactions"].append(txn_id)
        redis_client.set(
            f"{CITIZENS_PREFIX}{citizen_ids[i]}", serialize_for_db(citizen)
        )

        vendor["wallet_info"]["balance"] += amount
        if "transactions" not in vendor["wallet_info"]:
            vendor["wallet_info"]["transactions"] = []

        vendor["wallet_info"]["transactions"].append(txn_id)
        redis_client.set(f"{VENDORS_PREFIX}{vendor_id}", serialize_for_db(vendor))

        print(
            f"Created purchase: {citizen['account_info']['name']} to {vendor['business_info']['business_name']} (₹{amount})"
        )
        transaction_count += 1

print(
    f"\nSeeding completed!\n"
    f"  - Citizens created: {len(citizen_ids)}\n"
    f"  - Vendors created: {len(vendor_ids)}\n"
    f"  - Government entities created: {len(govt_ids)}\n"
    f"  - Schemes created: {len(scheme_ids)}\n"
    f"  - Transactions created: {transaction_count}"
)
EOF
)

# Check if script is running inside Docker container
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "$PYTHON_SCRIPT" | docker exec -i $(docker compose ps -q api) python -
else
    echo "$PYTHON_SCRIPT" | python -
fi

echo ""
echo "Test accounts created successfully!"
echo "==================================="
echo "Citizens:"
echo "  - Aadhar ID Number: 123456789012 / Password: citizen@123 (Areeb Ahmed)"
echo "  - Aadhar ID Number: 234567890123 / Password: citizen@123 (Shivansh Karan)"
echo "  - Aadhar ID Number: 345678901234 / Password: citizen@123 (Alfiya Fatima)"
echo ""
echo "Vendors:"
echo "  - Business ID: GSTIN22AAAAA1111Z / Password: vendor@123 (Malhotra Grocery Mart)"
echo "  - Business ID: GSTIN09BBBBB2222Y / Password: vendor@123 (MedPlus Pharmacy)"
echo "  - Business ID: GSTIN19CCCCC3333X / Password: vendor@123 (Khan Kirana Store)"
echo ""
echo "Government Entities:"
echo "  - Govt ID: DOPT0001 / Password: govt@123 (Ministry of Social Justice)"
echo "  - Govt ID: KARD0002 / Password: govt@123 (Karnataka Rural Development)"
echo "  - Govt ID: DELSW003 / Password: govt@123 (Delhi Social Welfare Department)"
