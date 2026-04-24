import os
import sys
# Add current directory to path so we can import our modules
sys.path.append(os.getcwd())

from backend.database.firebase_client import db_client
from dotenv import load_dotenv

load_dotenv()

print("\n--- FIREBASE STATUS CHECK ---")
print(f"Service Account Path: {os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')}")
print(f"Database URL: {os.getenv('FIREBASE_DATABASE_URL')}")

if db_client.is_firebase:
    print("\n✅ STATUS: CONNECTED TO REAL FIREBASE")
    print("Your data SHOULD be visible in the Firebase Console.")
else:
    print("\n❌ STATUS: RUNNING IN MOCK MODE (In-Memory)")
    print("Your data is NOT reaching the cloud. The key file might still be unreadable.")

# Test a write to be 100% sure
try:
    db_client.set_data("status_check", {"last_checked": "now", "connection": "verified"})
    print("✅ TEST WRITE: Successful.")
except Exception as e:
    print(f"❌ TEST WRITE FAILED: {e}")

print("-----------------------------\n")
