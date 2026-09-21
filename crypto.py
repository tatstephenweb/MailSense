#functions for encrypting and decrypting user email data before storing to database
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("ENCRYPTION_KEY")

#this function will encrypt the data (sender, snippet, and subject) before storing to the database
def encrypt_text(sender, subject, snippet):
    cipher = Fernet(key)
    #text = "Welcome to this platform"
    datas = [sender, subject, snippet]
    result = []
    for data in datas:
        encrypted = cipher.encrypt(data.encode())
        result.append(encrypted.decode())
    return result

#this function will take encrypted data from the database, decrypt it before being revealed to the frontend
def decrypt_text(data):
    cipher = Fernet(key)
    encrypted = data
    decrypted = cipher.decrypt(encrypted).decode()
    #print(f"encrypted {decrypted}")
    return decrypted
