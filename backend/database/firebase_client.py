import os
import json
import logging
from typing import Callable, Optional
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv # Added this

load_dotenv() # Load this BEFORE using os.getenv

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self):
        self.is_firebase = False
        self.mock_db = {}
        self.listeners = []
        
        firebase_sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        firebase_db_url = os.getenv("FIREBASE_DATABASE_URL")

        if firebase_sa_path and os.path.exists(firebase_sa_path) and firebase_db_url:
            try:
                cred = credentials.Certificate(firebase_sa_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': firebase_db_url
                })
                self.is_firebase = True
                logger.info("Firebase Realtime DB successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase Admin SDK: {e}. Falling back to in-memory DB.")
        else:
            logger.warning("Firebase credentials not found or empty. Using in-memory mock database.")

    def set_data(self, path: str, data: dict):
        if self.is_firebase:
            ref = db.reference(path)
            ref.set(data)
        else:
            # Simple path setting logic for mock
            keys = path.strip("/").split("/")
            current = self.mock_db
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = data
            
            # Trigger mock listeners
            for listener_path, callback in self.listeners:
                if path.startswith(listener_path):
                    # Simulate an Event object
                    class MockEvent:
                        def __init__(self, e_path, e_data):
                            self.path = e_path
                            self.data = e_data
                            self.event_type = 'put'
                    
                    # Create an event representing the change
                    event = MockEvent("/" + keys[-1], data)
                    callback(event)

    def update_data(self, path: str, data: dict):
        if self.is_firebase:
            ref = db.reference(path)
            ref.update(data)
        else:
            # Simple merge logic
            keys = path.strip("/").split("/")
            current = self.mock_db
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            if keys[-1] not in current or not isinstance(current[keys[-1]], dict):
                current[keys[-1]] = {}
                
            current[keys[-1]].update(data)
            
            # Trigger mock listeners
            for listener_path, callback in self.listeners:
                if path.startswith(listener_path):
                    class MockEvent:
                        def __init__(self, e_path, e_data):
                            self.path = e_path
                            self.data = e_data
                            self.event_type = 'update'
                    event = MockEvent("/" + keys[-1], data)
                    callback(event)

    def get_data(self, path: str) -> Optional[dict]:
        if self.is_firebase:
            ref = db.reference(path)
            return ref.get()
        else:
            keys = path.strip("/").split("/")
            current = self.mock_db
            for key in keys:
                if key not in current:
                    return None
                current = current[key]
            return current

    def listen(self, path: str, callback: Callable):
        """
        Listens to changes at a specific path. 
        callback should accept an 'event' parameter.
        """
        if self.is_firebase:
            ref = db.reference(path)
            ref.listen(callback)
            logger.info(f"Firebase Listener attached to {path}")
        else:
            self.listeners.append((path, callback))
            logger.info(f"Mock DB Listener attached to {path}")

# Initialize a singleton client
db_client = DatabaseClient()
