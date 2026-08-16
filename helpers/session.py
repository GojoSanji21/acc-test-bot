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

import os
import random
import logging
import re
from pyrogram import Client
from config import API_ID, API_HASH

logger = logging.getLogger("TGStorageBot.helpers.session")

def parse_proxy_line(line: str) -> dict:
    """
    Parses a proxy string line into a Pyrogram compatible proxy dictionary.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    if line.startswith("socks5://"):
        cleaned = line[9:]
        if "@" in cleaned:
            auth, host_port = cleaned.split("@", 1)
            username, password = auth.split(":", 1) if ":" in auth else (auth, "")
            host, port = host_port.split(":", 1) if ":" in host_port else (host_port, "1080")
            return {
                "scheme": "socks5",
                "hostname": host,
                "port": int(port),
                "username": username,
                "password": password
            }
        else:
            host, port = cleaned.split(":", 1) if ":" in cleaned else (cleaned, "1080")
            return {
                "scheme": "socks5",
                "hostname": host,
                "port": int(port)
            }

    parts = line.split(":")
    if len(parts) == 4:
        return {
            "scheme": "socks5",
            "hostname": parts[0],
            "port": int(parts[1]),
            "username": parts[2],
            "password": parts[3]
        }
    elif len(parts) == 2:
        return {
            "scheme": "socks5",
            "hostname": parts[0],
            "port": int(parts[1])
        }

    return None

def load_proxies_from_file(filepath: str = "proxies.txt") -> tuple[list, str]:
    proxies = []
    if not os.path.exists(filepath):
        return proxies, f"File '{filepath}' not found on server."

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            parsed = parse_proxy_line(line)
            if parsed:
                proxies.append(parsed)

        if not proxies:
            return proxies, f"File '{filepath}' exists but has 0 valid/active proxy lines."
        return proxies, ""
    except Exception as e:
        return proxies, f"Failed to read file '{filepath}': {str(e)}"

def load_proxies_from_env() -> tuple[list, str]:
    proxies = []
    env_found = False

    for env_name in ["PROXY", "PROXIES"]:
        env_val = os.getenv(env_name)
        if env_val:
            env_found = True
            lines = re.split(r"[,\n]+", env_val)
            for line in lines:
                parsed = parse_proxy_line(line)
                if parsed:
                    proxies.append(parsed)

    if not env_found:
        return proxies, "Environment variables PROXY or PROXIES are not defined."
    if env_found and not proxies:
        return proxies, "Environment variables PROXY or PROXIES are defined but contains no valid proxy strings."

    return proxies, ""

def get_random_proxy() -> tuple[dict, str]:
    """
    Selects a random proxy from environment variables or proxies.txt file.
    Returns a tuple of (proxy_dict, explanation_or_error_string).
    """
    env_proxies, env_err = load_proxies_from_env()
    if env_proxies:
        selected = random.choice(env_proxies)
        msg = f"Successfully loaded proxy from environment: {selected['hostname']}:{selected['port']}"
        logger.info(msg)
        return selected, msg

    file_proxies, file_err = load_proxies_from_file()
    if file_proxies:
        selected = random.choice(file_proxies)
        msg = f"Successfully loaded proxy from proxies.txt: {selected['hostname']}:{selected['port']}"
        logger.info(msg)
        return selected, msg

    full_error_explanation = (
        f"Could not load any proxy.\n"
        f"- Environment Proxy Status: {env_err}\n"
        f"- File Proxy Status: {file_err}"
    )
    logger.warning(full_error_explanation)
    return None, full_error_explanation

def create_pyrogram_client(session_name: str, session_string: str = None, proxy: dict = None, custom_api: dict = None) -> Client:
    """
    Initializes an optimized Pyrogram Client in-memory.
    Note: 'ipv6=False' has been added to bypass slow IPv6 connection attempts and speed up OTP requests!
    """
    client_api_id = API_ID
    client_api_hash = API_HASH

    if custom_api:
        client_api_id = custom_api.get("api_id", client_api_id)
        client_api_hash = custom_api.get("api_hash", client_api_hash)

    logger.info(f"Creating optimized Pyrogram Client: API_ID={client_api_id}, session_name={session_name}, ipv6=False, proxy={proxy}")

    client = Client(
        name=session_name,
        api_id=client_api_id,
        api_hash=client_api_hash,
        session_string=session_string,
        proxy=proxy,
        ipv6=False,
        in_memory=True
    )
    return client

import socket

DC_IPS = {
    1: "149.154.175.50",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.165"
}

import sqlite3
from pathlib import Path

def generate_telethon_sqlite(session_str: str, phone_number: str, output_dir: Path | str) -> str:
    """
    Generates a Telethon .session SQLite file from a Pyrogram v2 Session string.
    Returns the file path of the generated database.
    """
    import base64
    import struct
    import binascii

    session_str = session_str.strip()
    missing_padding = len(session_str) % 4
    if missing_padding:
        session_str += '=' * (4 - missing_padding)

    try:
        decoded_bytes = base64.urlsafe_b64decode(session_str)
        if len(decoded_bytes) != 271:
            return None

        dc_id, api_id, test_mode, auth_key, user_id, is_bot = struct.unpack('>BI?256sQ?', decoded_bytes)
        ip = DC_IPS.get(dc_id, "149.154.167.51")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"{phone_number}.session"

        conn = sqlite3.connect(out_path)
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE version (version integer primary key);")
        cursor.execute("CREATE TABLE sessions (dc_id integer primary key, server_address text, port integer, auth_key blob, takeout_id integer);")
        cursor.execute("CREATE TABLE entities (id integer primary key, hash integer not null, username text, phone integer, name text, date integer);")

        cursor.execute("INSERT INTO version VALUES (7);")
        cursor.execute("INSERT INTO sessions (dc_id, server_address, port, auth_key, takeout_id) VALUES (?, ?, 443, ?, 0);", (dc_id, ip, auth_key))

        conn.commit()
        conn.close()

        return str(out_path)

    except (Exception, binascii.Error) as e:
        logger.debug(f"Failed to generate Telethon sqlite: {e}")
        return None

def pyrogram_to_telethon(session_str: str) -> str:
    """
    Converts a Pyrogram v2 Session string to a Telethon StringSession string.
    """
    import base64
    import struct

    session_str = session_str.strip()
    # Pyrogram session strings are Base64 but lack padding sometimes
    missing_padding = len(session_str) % 4
    if missing_padding:
        session_str += '=' * (4 - missing_padding)

    import binascii
    try:
        decoded_bytes = base64.urlsafe_b64decode(session_str)
        # Unpack Pyrogram v2 string format: >BI?256sQ? (length = 271)
        if len(decoded_bytes) != 271:
            return None

        dc_id, api_id, test_mode, auth_key, user_id, is_bot = struct.unpack('>BI?256sQ?', decoded_bytes)

        # Determine IP from dc_id
        ip = DC_IPS.get(dc_id, "149.154.167.51") # Default to DC 2 if unknown
        ip_bytes = socket.inet_aton(ip)

        # Pack into Telethon format: >B4sH256s (IPv4)
        telethon_packed = struct.pack('>B4sH256s', dc_id, ip_bytes, 443, auth_key)

        return "1" + base64.urlsafe_b64encode(telethon_packed).decode()
    except (Exception, binascii.Error) as e:
        logger.debug(f"Failed to parse as Pyrogram session string: {e}")
        return None

def telethon_to_pyrogram(session_str: str) -> str:
    """
    Converts a Telethon StringSession string to a Pyrogram session string if possible.
    If it's already a Pyrogram session string or invalid, returns None.
    """
    import base64
    import struct

    session_str = session_str.strip()
    if not session_str.startswith("1"):
        return None

    try:
        encoded_data = session_str[1:]
        # Pad base64 encoded data
        import binascii
        encoded_data += "=" * (-len(encoded_data) % 4)

        try:
            decoded_bytes = base64.urlsafe_b64decode(encoded_data)
        except (Exception, binascii.Error):
            decoded_bytes = base64.b64decode(encoded_data)

        # Telethon unpacked length:
        # >B4sH256s -> 1 + 4 + 2 + 256 = 263 bytes (IPv4)
        # >B16sH256s -> 1 + 16 + 2 + 256 = 275 bytes (IPv6)
        if len(decoded_bytes) == 263:
            ip_len = 4
        elif len(decoded_bytes) == 275:
            ip_len = 16
        else:
            return None

        dc_id, ip_bytes, port, auth_key = struct.unpack(f'>B{ip_len}sH256s', decoded_bytes)

        # Pack into Pyrogram v2 string format:
        # >BI?256sQ?
        pyro_packed = struct.pack(
            '>BI?256sQ?',
            dc_id,
            0,      # api_id
            False,  # test_mode
            auth_key,
            0,      # user_id
            False   # is_bot
        )
        return base64.urlsafe_b64encode(pyro_packed).decode().rstrip("=")
    except Exception as e:
        logger.debug(f"Failed to parse as Telethon session string: {e}")
        return None

def normalize_session_string(session_str: str) -> str:
    """
    Checks if session_str is a Telethon session string and converts it to Pyrogram format.
    Otherwise, returns the original session_str.
    """
    session_str = session_str.strip()
    if not session_str:
        return session_str

    if session_str.startswith("1"):
        converted = telethon_to_pyrogram(session_str)
        if converted:
            logger.info("Successfully converted Telethon StringSession to Pyrogram format.")
            return converted

    return session_str
