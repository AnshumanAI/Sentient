# server/mcp-hub/gdrive/generate_google_token.py

import asyncio
import os
import json
from dotenv import load_dotenv
import motor.motor_asyncio
from google_auth_oauthlib.flow import InstalledAppFlow

# --- Configuration ---
CREDENTIALS_FILE = "server/mcp-hub/credentials.json"
ENV_FILE = "server/.env"

# This scope allows for full read/write access to Google Drive files.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Load environment variables from .env file
if not os.path.exists(ENV_FILE):
    print(f"Error: The .env file was not found. Please create it from .env.template.")
    exit()
load_dotenv(ENV_FILE)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

if not all([MONGO_URI, MONGO_DB_NAME]):
    print("Error: MONGO_URI and MONGO_DB_NAME must be set in your .env file.")
    exit()

async def main():
    """
    Runs the OAuth 2.0 flow to get a token and saves it to MongoDB.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: Credentials file not found at '{CREDENTIALS_FILE}'")
        print("Please download it from your Google Cloud Console for a 'Desktop App' and place it here.")
        return

    user_id = input("Enter a unique User ID for this profile (e.g., 'sarthak', 'user01'): ").strip()
    if not user_id:
        print("User ID cannot be empty.")
        return

    print("\nStarting Google Authentication flow for Google Drive...")
    print("Your web browser will open for you to log in and grant permissions.")

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\nAuthentication successful!")
    token_info = json.loads(creds.to_json())

    print(f"Connecting to MongoDB at {MONGO_URI}...")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        users_collection = db["users"]
        
        result = await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"userId": user_id, "google_token": token_info}},
            upsert=True
        )

        if result.upserted_id:
            print(f"\nSuccessfully created new user profile with ID: {user_id}")
        else:
            print(f"\nSuccessfully updated token for existing user with ID: {user_id}")
        print("You can now use this User ID in your MCP client.")
    except Exception as e:
        print(f"\nAn error occurred while saving to MongoDB: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())