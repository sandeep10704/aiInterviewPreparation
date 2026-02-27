import firebase_admin
from firebase_admin import credentials, auth,firestore
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SERVICE_ACCOUNT_PATH = BASE_DIR / "firebase-key.json"

cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def verify_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        return None