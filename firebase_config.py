"""
Firebase Configuration Module
"""
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Load environment variables
load_dotenv()

FIREBASE_CONFIG = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.getenv('FIREBASE_APP_ID'),
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
}

SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH', './firebase-service-account-key.json')


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            # Initialize with service account
            if os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
                cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized with Service Account")
            else:
                print(f"⚠️  Service Account file not found: {SERVICE_ACCOUNT_KEY_PATH}")
                print("📝 Download from: Firebase Console -> Project Settings -> Service Accounts")
                print("⚠️  Running in DEMO MODE - Features limited to local testing")
                return False
        return True
    except Exception as e:
        print(f"⚠️  Firebase initialization warning: {str(e)}")
        print("⚠️  Running in DEMO MODE - Features limited to local testing")
        return False


def get_firestore_client():
    """Get Firestore client instance"""
    return firestore.client()


def get_auth_instance():
    """Get Firebase Auth instance"""
    return auth
