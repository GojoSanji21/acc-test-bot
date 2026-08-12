# =====================================================================================##
#
#  ██╗░░██╗███╗░░██╗██████╗░░█████╗░████████╗███████╗██████╗░
#  ██║░░██║████╗░██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
#  ██║░░██║██╔██╗██║██████╔╝███████║░░░██║░░░█████╗░░██║░░██║
#  ██║░░██║██║╚████║██╔══██╗██╔══██║░░░██║░░░██╔══╝░░██║░░██║
#  ╚█████╔╝██║░╚███║██║░░██║██║░░██║░░░██║░░░███████╗██████╔╝
#  ░╚════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═════╝░
#
#  ░██████╗░██████╗░██████╗░███████╗██████╗░
#  ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
#  ██║░░░░░██║░░░██║██║░░██║█████╗░░██████╔╝
#  ██║░░░░░██║░░░██║██║░░██║██╔══╝░░██╔══██╗
#  ╚██████╗╚██████╔╝██████╔╝███████╗██║░░██║
#  ░╚═════╝░╚═════╝░╚═════╝░╚══════╝╚═╝░░╚═╝
#
#                         ✨ MADE BY UNRATED CODER ✨
#                  Join Updates Channel: https://t.me/UNRATED_CODER
#=====================================================================================##

import logging
from .connection import accounts_collection, proxies_collection

logger = logging.getLogger("TGStorageBot.database.methods")

async def save_account(phone: str, encrypted_session: str, user_id: int, proxy: dict = None, custom_api: dict = None, profile_name: str = None) -> bool:
    """
    Saves or updates an authorized Telegram account in MongoDB for a specific user.
    """
    try:
        document = {
            "phone": phone,
            "user_id": user_id,
            "encrypted_session": encrypted_session,
            "proxy": proxy,
            "custom_api": custom_api,
            "profile_name": profile_name,
        }
        await accounts_collection.update_one(
            {"phone": phone, "user_id": user_id},
            {"$set": document},
            upsert=True
        )
        logger.info(f"Account for {phone} (user_id {user_id}) saved successfully to MongoDB.")
        return True
    except Exception as e:
        logger.error(f"Failed to save account for {phone} (user_id {user_id}): {e}")
        return False

async def get_account(phone: str, user_id: int) -> dict:
    """
    Retrieves an account by phone number and user_id.
    """
    try:
        return await accounts_collection.find_one({"phone": phone, "user_id": user_id})
    except Exception as e:
        logger.error(f"Failed to get account {phone} (user_id {user_id}): {e}")
        return None

async def delete_account(phone: str, user_id: int) -> bool:
    """
    Deletes an account by phone number and user_id.
    """
    try:
        result = await accounts_collection.delete_one({"phone": phone, "user_id": user_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Failed to delete account {phone} (user_id {user_id}): {e}")
        return False

async def delete_all_accounts(user_id: int) -> int:
    """
    Deletes all accounts for a specific user_id.
    Returns the number of deleted accounts.
    """
    try:
        result = await accounts_collection.delete_many({"user_id": user_id})
        return result.deleted_count
    except Exception as e:
        logger.error(f"Failed to delete all accounts for user_id {user_id}: {e}")
        return 0

async def get_all_accounts(user_id: int) -> list:
    """
    Retrieves all saved accounts for a specific user_id.
    """
    try:
        cursor = accounts_collection.find({"user_id": user_id})
        return await cursor.to_list(length=1000)
    except Exception as e:
        logger.error(f"Failed to retrieve all accounts for user_id {user_id}: {e}")
        return []

async def save_proxy(proxy_str: str) -> bool:
    """
    Saves a proxy string into MongoDB collection of proxy pools.
    """
    try:
        await proxies_collection.update_one(
            {"proxy_str": proxy_str},
            {"$set": {"proxy_str": proxy_str}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save proxy string {proxy_str}: {e}")
        return False

async def get_all_db_proxies() -> list:
    """
    Retrieves all SOCKS5 proxies saved in MongoDB.
    """
    try:
        cursor = proxies_collection.find()
        docs = await cursor.to_list(length=1000)
        return [d["proxy_str"] for d in docs if "proxy_str" in d]
    except Exception as e:
        logger.error(f"Failed to get db proxies: {e}")
        return []
