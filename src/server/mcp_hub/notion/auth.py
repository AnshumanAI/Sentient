import os
import json
import base64
from typing import Dict, Optional

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import motor.motor_asyncio
from notion_client import AsyncClient

from fastmcp import Context
from fastmcp.exceptions import ToolError


# Load from main server .env, which is two levels up



MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
AES_SECRET_KEY_HEX = os.getenv("AES_SECRET_KEY")
AES_IV_HEX = os.getenv("AES_IV")

AES_SECRET_KEY: Optional[bytes] = bytes.fromhex(AES_SECRET_KEY_HEX) if AES_SECRET_KEY_HEX and len(AES_SECRET_KEY_HEX) == 64 else None
AES_IV: Optional[bytes] = bytes.fromhex(AES_IV_HEX) if AES_IV_HEX and len(AES_IV_HEX) == 32 else None

def aes_decrypt(encrypted_data: str) -> str:
    if not AES_SECRET_KEY or not AES_IV:
        raise ValueError("AES encryption keys are not configured in the environment.")
    backend = default_backend()
    cipher = Cipher(algorithms.AES(AES_SECRET_KEY), modes.CBC(AES_IV), backend=backend)
    decryptor = cipher.decryptor()
    encrypted_bytes = base64.b64decode(encrypted_data)
    decrypted = decryptor.update(encrypted_bytes) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted) + unpadder.finalize()
    return unpadded_data.decode()

# Establish a single, reusable connection to MongoDB
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]
users_collection = db["user_profiles"]

def get_user_id_from_context(ctx: Context) -> str:
    http_request = ctx.get_http_request()
    if not http_request:
        raise ToolError("HTTP request context is not available.")
    user_id = http_request.headers.get("X-User-ID")
    if not user_id:
        raise ToolError("Authentication failed: 'X-User-ID' header is missing.")
    return user_id

async def get_notion_creds(user_id: str) -> Dict[str, str]:
    """Fetches Notion credentials (token) from MongoDB."""
    user_doc = await users_collection.find_one({"user_id": user_id})

    if not user_doc or not user_doc.get("userData"):
        raise ToolError(f"User profile or userData not found for user_id: {user_id}.")

    notion_data = user_doc["userData"].get("integrations", {}).get("notion")

    if not notion_data or not notion_data.get("connected") or "credentials" not in notion_data:
        raise ToolError(f"Notion integration not connected or credentials missing for {user_id}.")

    try:
        decrypted_creds_str = aes_decrypt(notion_data["credentials"])
        token_info = json.loads(decrypted_creds_str)
    except Exception as e:
        raise ToolError(f"Failed to decrypt or parse token for Notion: {e}")

    if "token" not in token_info:
        raise ToolError("Invalid token data in database for Notion. Re-authentication may be required.")

    return token_info

def authenticate_notion(creds: Dict[str, str]) -> AsyncClient:
    """Authenticates and returns the Notion async client."""
    return AsyncClient(auth=creds["token"])