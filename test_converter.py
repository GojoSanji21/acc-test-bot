import sys
import struct
import base64
sys.path.append('.')
from plugins.add_account import convert_telethon_string_to_pyrogram

# Create a dummy telethon string for testing
dc_id = 2
ip_bytes = b'\x95\xd5\xc1X' # some dummy IP
port = 443
auth_key = b'A' * 256
packed = struct.pack(">B4sH256s", dc_id, ip_bytes, port, auth_key)
b64_telethon = base64.urlsafe_b64encode(packed).decode().rstrip("=")
telethon_string = f"1{b64_telethon}"

try:
    pyrogram_string = convert_telethon_string_to_pyrogram(telethon_string, 6)
    print("Successfully converted.")
    print(f"Telethon String: {telethon_string}")
    print(f"Pyrogram String: {pyrogram_string}")

    # decode pyrogram string to verify
    decoded = base64.urlsafe_b64decode(pyrogram_string + "==")
    p_dc_id, p_api_id, p_test_mode, p_auth_key, p_user_id, p_is_bot = struct.unpack(">BI?256sQ?", decoded)
    assert p_dc_id == dc_id
    assert p_auth_key == auth_key
    assert p_user_id == 9999
    assert p_api_id == 6
    print("Verification passed!")
except Exception as e:
    print(f"Failed: {e}")
