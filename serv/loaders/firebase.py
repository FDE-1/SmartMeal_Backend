import firebase_admin
from firebase_admin import credentials
import os, json
from dotenv import load_dotenv

load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "AIzaSyBAeb4LtWX3lHdiqA6glTHEBxyFRYWU_Zo")

current_dir = os.path.dirname(os.path.abspath(__file__))
firebase_key_path = os.path.join(current_dir, "smartmeal-62b08-firebase-adminsdk-fbsvc-1e493fd71f.json")
with open(firebase_key_path, 'r') as file:
    firebase = json.load(file)

FIREBASE_API_KEY = firebase['private_key_id']
private_key = firebase['private_key']

# Replace literal '\n' with actual newlines
if private_key:
    firebase['private_key'] = private_key.replace('\\n', '\n')
#a changer
cred = credentials.Certificate(firebase)

firebase_app = firebase_admin.initialize_app(cred)