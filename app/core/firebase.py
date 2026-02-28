import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

from app.core.config import settings   # your BaseSettings config


# ---------- Initialize Firebase ----------

if not firebase_admin._apps:
    if not settings.FIREBASE_CREDENTIALS:
        raise ValueError("FIREBASE_CREDENTIALS not found in environment")

    cred_dict = json.loads(settings.FIREBASE_CREDENTIALS)
    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred)


# ---------- Firestore Client ----------
db = firestore.client()


# ---------- Token Verification ----------
def verify_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        return None