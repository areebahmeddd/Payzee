import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define Firestore collections
citizens_collection = db.collection("citizens")
vendors_collection = db.collection("vendors")
governments_collection = db.collection("governments")
schemes_collection = db.collection("schemes")
transactions_collection = db.collection("transactions")
