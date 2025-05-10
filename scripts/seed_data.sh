#!/bin/bash

echo "Seeding test data into Redis..."
echo "==============================="
echo ""

check_docker() {
    echo "Checking Docker status..."

    if command -v docker &> /dev/null; then
        docker info > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "Docker is running!"
            echo ""
            return 0
        else
            echo "Docker is installed but not running. Please start Docker."
            return 1
        fi
    else
        echo "Docker not installed. Please install Docker."
        return 1
    fi
}

check_services() {
    echo "Checking Docker Compose services..."

    if ! command -v docker &> /dev/null; then
        echo "Docker not found. Cannot check services."
        return 1
    fi

    if [ ! -f "../docker-compose.yaml" ]; then
        echo "docker-compose.yaml not found in parent directory!"
        return 1
    fi

    CONTAINERS_RUNNING=$(docker ps --filter "name=payzee" --format "{{.Names}}" | wc -l)

    if [ "$CONTAINERS_RUNNING" -eq 0 ]; then
        echo "Starting Payzee containers..."

        cd ..
        export COMPOSE_BAKE=true
        docker compose up -d

        if [ $? -ne 0 ]; then
            echo "Failed to start Docker Compose services."
            return 1
        fi

        echo "Services started successfully."
        echo "Waiting for services to initialize..."
        sleep 10
    else
        echo "All services are running!"
        echo ""
    fi

    return 0
}

check_redis() {
    echo "Checking Redis connection..."

    MAX_RETRIES=5
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if docker exec payzee-redis-1 redis-cli PING | grep -q 'PONG'; then
            echo "Redis connection successful!"
            echo ""
            return 0
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            echo "Retrying Redis connection ($RETRY_COUNT/$MAX_RETRIES)..."
            sleep 3
        fi
    done

    echo "Failed to connect to Redis after $MAX_RETRIES attempts."
    return 1
}

seed_data() {
    read -r -d '' SEED_SCRIPT << 'EOF'
import json
import uuid
import time
import random
import hashlib
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

import redis
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def serialize_for_db(data):
    return json.dumps(data)

def deserialize_from_db(data):
    return json.loads(data)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

print("Clearing Redis database...")
redis_client.flushall()
redis_client.ping()
print("Database cleared.\n")

print("Creating citizens...")
citizens = [
    {
        "name": "Areeb Ahmed",
        "email": "areeb@example.com",
        "password": "admin@123",
        "phone": "+91 9876543210",
        "address": "42, Linking Road, Bandra West, Mumbai, Maharashtra, 400050",
        "id_type": "Aadhaar",
        "id_number": "123456789012"
    },
    {
        "name": "Shivansh Karan",
        "email": "shivansh@example.com",
        "password": "admin@123",
        "phone": "+91 8765432109",
        "address": "15, MG Road, Bengaluru, Karnataka, 560001",
        "id_type": "Aadhaar",
        "id_number": "234567890123"
    },
    {
        "name": "Alfiya Fatima",
        "email": "alfiya@example.com",
        "password": "admin@123",
        "phone": "+91 7654321098",
        "address": "78, Civil Lines, Delhi, 110054",
        "id_type": "Aadhaar",
        "id_number": "345678901234"
    }
]

citizen_ids = []
for citizen_data in citizens:
    citizen_id = str(uuid.uuid4())
    citizen_ids.append(citizen_id)

    hashed_pw = hash_password(citizen_data['password'])

    citizen = {
        "account_info": {
            "id": citizen_id,
            "name": citizen_data["name"],
            "email": citizen_data["email"],
            "password": hashed_pw,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_type": "citizen"
        },
        "personal_info": {
            "phone": citizen_data["phone"],
            "address": citizen_data["address"],
            "id_type": citizen_data["id_type"],
            "id_number": citizen_data["id_number"]
        },
        "wallet_info": {
            "govt_wallet": {"balance": random.randint(500, 5000), "transactions": []},
            "personal_wallet": {"balance": random.randint(500, 5000), "transactions": []}
        }
    }

    redis_client.set(f"{CITIZENS_PREFIX}{citizen_id}", serialize_for_db(citizen))
    redis_client.sadd(CITIZENS_SET, citizen_id)

    print(f"Added citizen: {citizen_data['name']}")

print("\nCreating vendors...")
vendors = [
    {
        "name": "Rajan Malhotra",
        "email": "grocerymart@example.com",
        "password": "admin@123",
        "business_name": "Malhotra Grocery Mart",
        "phone": "+91 9988776655",
        "address": "23, Krishna Market, Lajpat Nagar, New Delhi, 110024",
        "business_id": "GSTIN22AAAAA1111Z",
        "license_type": "private"
    },
    {
        "name": "Priya Sharma",
        "email": "medplus@example.com",
        "password": "admin@123",
        "business_name": "MedPlus Pharmacy",
        "phone": "+91 8877665544",
        "address": "56, Sector 18, Noida, Uttar Pradesh, 201301",
        "business_id": "GSTIN09BBBBB2222Y",
        "license_type": "public"
    },
    {
        "name": "Abdul Khan",
        "email": "kirana@example.com",
        "password": "admin@123",
        "business_name": "Khan Kirana Store",
        "phone": "+91 7766554433",
        "address": "10, Park Street, Kolkata, West Bengal, 700016",
        "business_id": "GSTIN19CCCCC3333X",
        "license_type": "government"
    }
]

vendor_ids = []
for vendor_data in vendors:
    vendor_id = str(uuid.uuid4())
    vendor_ids.append(vendor_id)

    hashed_pw = hash_password(vendor_data['password'])

    vendor = {
        "account_info": {
            "id": vendor_id,
            "name": vendor_data["name"],
            "email": vendor_data["email"],
            "password": hashed_pw,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_type": "vendor"
        },
        "business_info": {
            "business_name": vendor_data["business_name"],
            "phone": vendor_data["phone"],
            "address": vendor_data["address"],
            "business_id": vendor_data["business_id"],
            "license_type": vendor_data["license_type"]
        },
        "wallet_info": {
            "balance": random.randint(5000, 20000),
            "transactions": []
        }
    }

    redis_client.set(f"{VENDORS_PREFIX}{vendor_id}", serialize_for_db(vendor))
    redis_client.sadd(VENDORS_SET, vendor_id)

    print(f"Added vendor: {vendor_data['business_name']}")

print("\nCreating government entities...")
governments = [
    {
        "name": "Ministry of Social Justice",
        "email": "social.justice@gov.in",
        "password": "admin@123",
        "department": "Social Justice and Empowerment",
        "jurisdiction": "Central",
        "govt_id": "DOPT0001"
    },
    {
        "name": "Karnataka Rural Development",
        "email": "rural.dev@karnataka.gov.in",
        "password": "admin@123",
        "department": "Rural Development",
        "jurisdiction": "State",
        "govt_id": "KARD0002"
    },
    {
        "name": "Delhi Social Welfare Department",
        "email": "dsw@delhi.gov.in",
        "password": "admin@123",
        "department": "Social Welfare",
        "jurisdiction": "State",
        "govt_id": "DELSW003"
    }
]

govt_ids = []
for govt_data in governments:
    govt_id = str(uuid.uuid4())
    govt_ids.append(govt_id)

    hashed_pw = hash_password(govt_data['password'])

    govt = {
        "account_info": {
            "id": govt_id,
            "name": govt_data["name"],
            "email": govt_data["email"],
            "password": hashed_pw,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_type": "government"
        },
        "department_info": {
            "department": govt_data["department"],
            "jurisdiction": govt_data["jurisdiction"],
            "govt_id": govt_data["govt_id"]
        },
        "wallet_info": {
            "balance": random.randint(1000000, 10000000),
            "schemes": [],
            "transactions": []
        }
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
            "gender": "male",
            "state": "Maharashtra",
            "district": "Mumbai",
            "city": "Mumbai",
            "caste": "OBC",
            "annual_income": 100000
        },
        "tags": ["agriculture", "farmer-welfare", "income-support"]
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
            "gender": "female",
            "state": "Karnataka",
            "district": "Bangalore Rural",
            "city": "Doddaballapur",
            "caste": "SC",
            "annual_income": 300000
        },
        "tags": ["education", "scholarship", "rural"]
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
            "annual_income": 250000
        },
        "tags": ["health", "insurance", "poverty"]
    }
]

scheme_ids = []
for scheme_data in schemes:
    scheme_id = str(uuid.uuid4())
    scheme_ids.append(scheme_id)

    scheme = {
        "id": scheme_id,
        "name": scheme_data["name"],
        "description": scheme_data["description"],
        "govt_id": scheme_data["govt_id"],
        "amount": scheme_data["amount"],
        "eligibility_criteria": scheme_data["eligibility_criteria"],
        "tags": scheme_data["tags"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": scheme_data.get("status", "active"),
        "beneficiaries": []
    }

    redis_client.set(f"{SCHEMES_PREFIX}{scheme_id}", serialize_for_db(scheme))
    redis_client.sadd(SCHEMES_SET, scheme_id)

    govt_key = f"{GOVERNMENTS_PREFIX}{scheme_data['govt_id']}"
    govt_data = redis_client.get(govt_key)
    if govt_data:
        govt_dict = deserialize_from_db(govt_data)
        govt_dict['wallet_info']['schemes'].append(scheme_id)
        redis_client.set(govt_key, serialize_for_db(govt_dict))

    print(f"Added scheme: {scheme_data['name']}")

print("\nCreating transactions...")
transactions = []
transaction_count = 0

for scheme_id in scheme_ids:
    scheme_data = redis_client.get(f"{SCHEMES_PREFIX}{scheme_id}")
    scheme = deserialize_from_db(scheme_data)

    govt_data = redis_client.get(f"{GOVERNMENTS_PREFIX}{scheme['govt_id']}")
    govt = deserialize_from_db(govt_data)

    beneficiaries = random.sample(citizen_ids, random.randint(1, 2))

    for citizen_id in beneficiaries:
        if transaction_count >= 5:
            break

        txn_id = str(uuid.uuid4())

        citizen_data = redis_client.get(f"{CITIZENS_PREFIX}{citizen_id}")
        citizen = deserialize_from_db(citizen_data)

        transaction = {
            "id": txn_id,
            "from_id": scheme['govt_id'],
            "to_id": citizen_id,
            "amount": scheme['amount'],
            "tx_type": "government-to-citizen",
            "scheme_id": scheme['id'],
            "description": f"Disbursement for {scheme['name']}",
            "timestamp": (datetime.now() - timedelta(days=random.randint(5, 30))).isoformat(),
            "status": "completed"
        }

        redis_client.set(f"{TRANSACTIONS_PREFIX}{txn_id}", serialize_for_db(transaction))
        redis_client.sadd(TRANSACTIONS_SET, txn_id)

        citizen['wallet_info']['govt_wallet']['balance'] += scheme['amount']
        if 'transactions' not in citizen['wallet_info']['govt_wallet']:
            citizen['wallet_info']['govt_wallet']['transactions'] = []
        citizen['wallet_info']['govt_wallet']['transactions'].append(txn_id)
        redis_client.set(f"{CITIZENS_PREFIX}{citizen_id}", serialize_for_db(citizen))

        govt['wallet_info']['balance'] -= scheme['amount']
        if 'transactions' not in govt['wallet_info']:
            govt['wallet_info']['transactions'] = []
        govt['wallet_info']['transactions'].append(txn_id)
        redis_client.set(f"{GOVERNMENTS_PREFIX}{scheme['govt_id']}", serialize_for_db(govt))

        print(f"Created disbursement: {govt['account_info']['name']} to {citizen['account_info']['name']} (₹{scheme['amount']})")
        transaction_count += 1

remaining_transactions = 10 - transaction_count
transactions_per_citizen = max(1, remaining_transactions // len(citizen_ids))

for i in range(len(citizen_ids)):
    num_purchases = min(transactions_per_citizen, remaining_transactions)
    for _ in range(num_purchases):
        if transaction_count >= 10:
            break

        txn_id = str(uuid.uuid4())
        vendor_id = random.choice(vendor_ids)

        citizen_data = redis_client.get(f"{CITIZENS_PREFIX}{citizen_ids[i]}")
        citizen = deserialize_from_db(citizen_data)

        vendor_data = redis_client.get(f"{VENDORS_PREFIX}{vendor_id}")
        vendor = deserialize_from_db(vendor_data)

        amount = random.randint(100, 1000)

        if citizen['wallet_info']['personal_wallet']['balance'] < amount:
            continue

        transaction = {
            "id": txn_id,
            "from_id": citizen_ids[i],
            "to_id": vendor_id,
            "amount": amount,
            "tx_type": "citizen-to-vendor",
            "scheme_id": None,
            "description": f"Purchase at {vendor['business_info']['business_name']}",
            "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "status": "completed"
        }

        redis_client.set(f"{TRANSACTIONS_PREFIX}{txn_id}", serialize_for_db(transaction))
        redis_client.sadd(TRANSACTIONS_SET, txn_id)

        citizen['wallet_info']['personal_wallet']['balance'] -= amount
        if 'transactions' not in citizen['wallet_info']['personal_wallet']:
            citizen['wallet_info']['personal_wallet']['transactions'] = []
        citizen['wallet_info']['personal_wallet']['transactions'].append(txn_id)
        redis_client.set(f"{CITIZENS_PREFIX}{citizen_ids[i]}", serialize_for_db(citizen))

        vendor['wallet_info']['balance'] += amount
        if 'transactions' not in vendor['wallet_info']:
            vendor['wallet_info']['transactions'] = []
        vendor['wallet_info']['transactions'].append(txn_id)
        redis_client.set(f"{VENDORS_PREFIX}{vendor_id}", serialize_for_db(vendor))

        print(f"Created purchase: {citizen['account_info']['name']} to {vendor['business_info']['business_name']} (₹{amount})")
        transaction_count += 1

print("\nSeeding completed!")
EOF

    echo "Starting seeding process..."
    echo ""
    docker exec -i payzee-api-1 python3 -c "$SEED_SCRIPT"
}

main() {
    check_docker || exit 1
    check_services || exit 1
    check_redis || exit 1
    seed_data

    echo ""
    echo "Test accounts created successfully!"
    echo "==================================="
    echo "Citizens (login using ID Number):"
    echo "  - Aadhar ID Number: 123456789012 / Password: admin@123 (Areeb Ahmed)"
    echo "  - Aadhar ID Number: 234567890123 / Password: admin@123 (Shivansh Karan)"
    echo "  - Aadhar ID Number: 345678901234 / Password: admin@123 (Alfiya Fatima)"
    echo ""
    echo "Vendors (login using Business ID):"
    echo "  - Business ID: GSTIN22AAAAA1111Z / Password: admin@123 (Malhotra Grocery Mart)"
    echo "  - Business ID: GSTIN09BBBBB2222Y / Password: admin@123 (MedPlus Pharmacy)"
    echo "  - Business ID: GSTIN19CCCCC3333X / Password: admin@123 (Khan Kirana Store)"
    echo ""
    echo "Government Entities (login using Govt ID):"
    echo "  - Govt ID: DOPT0001 / Password: admin@123 (Ministry of Social Justice)"
    echo "  - Govt ID: KARD0002 / Password: admin@123 (Karnataka Rural Development)"
    echo "  - Govt ID: DELSW003 / Password: admin@123 (Delhi Social Welfare Department)"
}

main
