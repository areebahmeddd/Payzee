from sqlalchemy.orm import Session
from ..models import User, Vendor, Scheme, Transaction
from .data import users_data, vendors_data, schemes_data, transactions_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_users(db: Session) -> dict:
    """Seed users and return a mapping of aadhaar numbers to user IDs."""
    logger.info("Seeding users...")
    aadhaar_to_id = {}
    
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        db.flush()  # Flush to get the ID
        aadhaar_to_id[user_data["aadhaar_number"]] = user.id
    
    db.commit()
    logger.info(f"Seeded {len(users_data)} users")
    return aadhaar_to_id

def seed_vendors(db: Session) -> dict:
    """Seed vendors and return a mapping of vendor names to vendor IDs."""
    logger.info("Seeding vendors...")
    name_to_id = {}
    
    for vendor_data in vendors_data:
        vendor = Vendor(**vendor_data)
        db.add(vendor)
        db.flush()  # Flush to get the ID
        name_to_id[vendor_data["name"]] = vendor.id
    
    db.commit()
    logger.info(f"Seeded {len(vendors_data)} vendors")
    return name_to_id

def seed_schemes(db: Session) -> dict:
    """Seed schemes and return a mapping of scheme names to scheme IDs."""
    logger.info("Seeding schemes...")
    name_to_id = {}
    
    for scheme_data in schemes_data:
        scheme = Scheme(**scheme_data)
        db.add(scheme)
        db.flush()  # Flush to get the ID
        name_to_id[scheme_data["name"]] = scheme.id
    
    db.commit()
    logger.info(f"Seeded {len(schemes_data)} schemes")
    return name_to_id

def seed_transactions(db: Session, user_ids: dict, vendor_ids: dict, scheme_ids: dict):
    """Seed transactions using the provided ID mappings."""
    logger.info("Seeding transactions...")
    
    # Map transactions to their respective IDs
    transaction_mappings = [
        {
            "user_id": user_ids["123456789012"],  # Rahul Sharma
            "vendor_id": vendor_ids["Education Store"],
            "scheme_id": scheme_ids["PM Stationery Yojana 2024"]
        },
        {
            "user_id": user_ids["234567890123"],  # Priya Patel
            "vendor_id": vendor_ids["Rural Supplies Co"],
            "scheme_id": scheme_ids["Farmer Support Scheme"]
        },
        {
            "user_id": user_ids["345678901234"],  # Amit Kumar
            "vendor_id": vendor_ids["Tech Solutions Ltd"],
            "scheme_id": scheme_ids["Digital Literacy Program"]
        }
    ]
    
    for i, transaction_data in enumerate(transactions_data):
        transaction_data.update(transaction_mappings[i])
        transaction = Transaction(**transaction_data)
        db.add(transaction)
    
    db.commit()
    logger.info(f"Seeded {len(transactions_data)} transactions")

def seed_database(db: Session):
    """Main function to seed all data into the database."""
    try:
        # Seed in order of dependencies
        user_ids = seed_users(db)
        vendor_ids = seed_vendors(db)
        scheme_ids = seed_schemes(db)
        seed_transactions(db, user_ids, vendor_ids, scheme_ids)
        
        logger.info("Database seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise 