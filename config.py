from dotenv import load_dotenv
load_dotenv()
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
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TGStorageBot")

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8368366261:AAGd-1uLPo8HWxhO05ZLenu2oIZquYeGLOM")
API_ID = int(os.getenv("API_ID", "39800351"))
API_HASH = os.getenv("API_HASH", "2a6fbe5d5c92adf1b49f9667be3598c3")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://adilsh0137_db_user:E08VTbbalq1OQ44q@cluster0.s54nwax.mongodb.net/?appName=Naruto_new_season_bot")

# Parse Owner ID
OWNER_ID = int(os.getenv("OWNER_ID", "1683225887"))

# Custom Security Hybrid Algorithm
class CustomSecurity:
    def __init__(self, shift_pattern: list, secret_salt: str):
        # Shift pattern is a list of integers, e.g. [12, 4, 89, 31, 5, 76]
        self.shift_pattern = shift_pattern if shift_pattern else [7, 3, 9, 2]
        self.secret_salt = secret_salt if secret_salt else "default_salt_change_me"

        # Custom substitution map (Replaces Standard Base64)
        # Using non-hex characters (g to p) to avoid collision with 'a' through 'f' in hexadecimal.
        self.custom_map = {
            '0': 'g', '1': 'h', '2': 'i', '3': 'j', '4': 'k',
            '5': 'l', '6': 'm', '7': 'n', '8': 'o', '9': 'p'
        }
        self.reverse_map = {v: k for k, v in self.custom_map.items()}

    def encrypt(self, plain_text: str) -> str:
        if not plain_text:
            return ""
        # Layer 1: Salt addition and reversing the string
        salted_text = f"{plain_text}{self.secret_salt}"
        reversed_text = salted_text[::-1]

        # Layer 2: Custom Prime-Shift Cipher (ASCII Shifting)
        encrypted_chars = []
        pattern_len = len(self.shift_pattern)
        for i, char in enumerate(reversed_text):
            shift = self.shift_pattern[i % pattern_len]
            # ASCII value shift to a safe Unicode range
            shifted_char = chr((ord(char) + shift) % 1114112)
            encrypted_chars.append(shifted_char)

        temp_encrypted = "".join(encrypted_chars)

        # Layer 3: Convert to Hex and apply Custom Substitution Map
        hex_output = temp_encrypted.encode('utf-8').hex()
        final_output = []
        for char in hex_output:
            if char in self.custom_map:
                final_output.append(self.custom_map[char])
            else:
                final_output.append(char)

        return "".join(final_output)

    def decrypt(self, encrypted_text: str) -> str:
        if not encrypted_text:
            return ""
        # Layer 3 Reverse: Map substitution from custom map back to standard hex
        hex_chars = []
        for char in encrypted_text:
            if char in self.reverse_map:
                hex_chars.append(self.reverse_map[char])
            else:
                hex_chars.append(char)

        hex_string = "".join(hex_chars)
        temp_encrypted = bytes.fromhex(hex_string).decode('utf-8')

        # Layer 2 Reverse: Reverse ASCII shifting
        decrypted_chars = []
        pattern_len = len(self.shift_pattern)
        for i, char in enumerate(temp_encrypted):
            shift = self.shift_pattern[i % pattern_len]
            original_char = chr((ord(char) - shift) % 1114112)
            decrypted_chars.append(original_char)

        reversed_text = "".join(decrypted_chars)

        # Layer 1 Reverse: Reversal and salt removal
        original_with_salt = reversed_text[::-1]
        if original_with_salt.endswith(self.secret_salt):
            return original_with_salt[:-len(self.secret_salt)]
        else:
            raise ValueError("Decryption Failed: Custom logic key or salt is incorrect!")

# Load custom config keys
custom_shift_pattern_str = os.getenv("CUSTOM_SHIFT_PATTERN", "12,4,89,31,5,76")
custom_salt = os.getenv("CUSTOM_SALT", "MyPrivateBotSecureAccess10x")

try:
    custom_shift_pattern = [int(x.strip()) for x in custom_shift_pattern_str.split(",") if x.strip()]
except Exception as e:
    logger.error(f"Failed to parse CUSTOM_SHIFT_PATTERN. Using default shift pattern. Error: {e}")
    custom_shift_pattern = [12, 4, 89, 31, 5, 76]

# Initialize hybrid cryptor
cryptor = CustomSecurity(shift_pattern=custom_shift_pattern, secret_salt=custom_salt)

def encrypt_data(plain_text: str) -> str:
    return cryptor.encrypt(plain_text)

def decrypt_data(cipher_text: str) -> str:
    return cryptor.decrypt(cipher_text)
