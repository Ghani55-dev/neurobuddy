import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("config/firebase/neuro-ea867-firebase-adminsdk-fbsvc-9b1ab3e40d.json")
default_app = firebase_admin.initialize_app(cred)
