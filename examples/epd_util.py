from pathlib import Path
import subprocess
from PIL import Image

import requests
import base64
from datetime import datetime, timezone
import struct
import hashlib
import json
import os
import zlib
import sys
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import padding

request_id_prefix = "smartwizart-cli-app"
image_id_prefix = "image-"

def get_current_request_utc():
    request_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return request_utc

def send_device_register_request(api_url, request_id, request_utc, app_private_key, app_public_key):
    base64_encoded = base64.b64encode(app_public_key)
    base64_public_key = base64_encoded.decode("utf-8")
    device_register_request = {
        "request_id": request_id,
        "request_utc": request_utc,
        "command": "device_register_request",
        "public_key": base64_public_key
    }

    contents  = json.dumps(device_register_request, ensure_ascii=False, indent=4)
    signature = app_private_key.sign(contents.encode("utf-8"), asym_padding.PKCS1v15(), hashes.SHA256())

    base64_signature = base64.b64encode(signature).decode()
    headers = {
        "Content-Type": "application/json",
        "X-SmartWizArt-Signature": base64_signature,
    }

    try:
        response = requests.post(api_url, data=contents, headers=headers, timeout=60)
        print(f"Device register response: {response.status_code} {response.text}")
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return None

    return response

def send_device_unregister_request(api_url, request_id, request_utc, app_private_key):
    device_unregister_request = {"request_id": request_id, "request_utc": request_utc, "command": "device_unregister_request"}

    contents = json.dumps(device_unregister_request, ensure_ascii=False, indent=4)
    signature = app_private_key.sign(contents.encode("utf-8"), asym_padding.PKCS1v15(), hashes.SHA256())
    base64_signature = base64.b64encode(signature).decode()
    headers = {"Content-Type": "application/json", "X-SmartWizArt-Signature": base64_signature}

    try:
        response = requests.post(api_url, data=contents, headers=headers, timeout=60)
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException as e:
        return None

    return response

def send_device_config_request_request(api_url, request_id, request_utc, app_private_key, device_name=None, enable_matter_onoff_on_event=None, enable_matter_onoff_off_event=None, operation_mode=None, enable_matter_onoff_on_action=None, enable_matter_onoff_off_action=None):
    device_config_request = {"request_id": request_id, "request_utc": request_utc, "command": "device_config_request"}

    if device_name is not None:
        device_config_request["device_name"] = device_name
    if enable_matter_onoff_on_event is not None:
        device_config_request["enable_matter_onoff_on_event"] = enable_matter_onoff_on_event
    if enable_matter_onoff_off_event is not None:
        device_config_request["enable_matter_onoff_off_event"] = enable_matter_onoff_off_event
    if operation_mode is not None:
        device_config_request["enable_matter_onoff_operation_mode"] = operation_mode
    if enable_matter_onoff_on_action is not None:
        device_config_request["enable_matter_onoff_on_action"] = enable_matter_onoff_on_action
    if enable_matter_onoff_off_action is not None:
        device_config_request["enable_matter_onoff_off_action"] = enable_matter_onoff_off_action

    contents = json.dumps(device_config_request, ensure_ascii=False, indent=4)
    signature = app_private_key.sign(contents.encode("utf-8"), asym_padding.PKCS1v15(), hashes.SHA256())
    base64_signature = base64.b64encode(signature).decode()

    headers = {"Content-Type": "application/json", "X-SmartWizArt-Signature": base64_signature}
    try:
        response = requests.post(api_url, data=contents, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        print("send_device_config_request_request timeout...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return None

    return response

def send_get_device_status_request(api_url, request_id, request_utc, app_private_key):
    device_status_request = {"request_id": request_id, "request_utc": request_utc, "command": "get_device_status_request"}
    contents = json.dumps(device_status_request, ensure_ascii=False, indent=4)
    signature = app_private_key.sign(contents.encode("utf-8"), asym_padding.PKCS1v15(), hashes.SHA256())
    base64_signature = base64.b64encode(signature).decode()

    headers = {"Content-Type": "application/json","X-SmartWizArt-Signature": base64_signature}
    try:
        response = requests.post(api_url, data=contents, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        print("send_get_device_status_request timeout...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return None

    return response

def send_image_upload_request(api_url, request_id, request_utc, app_private_key, image_contents):
    base64_encoded = base64.b64encode(image_contents)
    base64_encoded_image = base64_encoded.decode("utf-8")

    image_upload_request = {"request_id": request_id, "request_utc": request_utc, "command": "image_upload_request", "contents": base64_encoded_image}

    contents = json.dumps(image_upload_request, ensure_ascii=False, indent=4)
    signature = app_private_key.sign(contents.encode("utf-8"), asym_padding.PKCS1v15(), hashes.SHA256())
    base64_signature = base64.b64encode(signature).decode()

    headers = {"Content-Type": "application/json", "X-SmartWizArt-Signature": base64_signature}
    try:
        response = requests.post(api_url, data=contents, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        print("send_image_upload_request timeout...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return None

    return response

def send_display_request(api_url, request_id, request_utc, app_private_key, file, user_name, user_comment):
    display_request = {"request_id": request_id, "request_utc": request_utc, "command": "display_request", "file": file, "user_name": user_name, "user_comment": user_comment}

    contents = json.dumps(display_request, ensure_ascii=False, indent=4).encode("utf-8")
    signature = app_private_key.sign(contents, asym_padding.PKCS1v15(), hashes.SHA256())
    base64_signature = base64.b64encode(signature).decode()

    headers = {"Content-Type": "application/json", "X-SmartWizArt-Signature": base64_signature}
    try:
        response = requests.post(api_url, data=contents, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        print("send_display_request timeout...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return None

    return response

def encrypt_aes_cbc(key: bytes, iv: bytes, plain_data: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_data) + padder.finalize()

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext

def decrypt_aes_cbc(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_data

def get_padding_size(decrypted_data: bytes) -> int:
    # padding size is determined by the value of the last byte of decrypted data
    padding_size = decrypted_data[-1]
    return padding_size

DATA_TYPE   = "S6SA"
X_OFFSET    = 0
Y_OFFSET    = 0
IMAGE_WIDTH       = 800
IMAGE_HEIGHT      = 480

def convert_image_to_s6(input_image_path, output_s6_path):
    dither_png = input_image_path.with_suffix(input_image_path.suffix + ".dither.png")
    output_image = Path(output_s6_path)

    # dither + remap
    current_dir = Path(__file__).resolve().parent
    palette_png_path = current_dir / "palette.png"
    subprocess.run([
        "convert",
        str(input_image_path),
        "-resize", f"{IMAGE_WIDTH}x{IMAGE_HEIGHT}!",
        "-colorspace", "RGB",
        "-dither", "FloydSteinberg",
        "-define", f"dither:diffusion-amount=100%",
        "-remap", str(palette_png_path),
        str(dither_png)
    ])

    img = Image.open(dither_png).convert("RGBA")
    width, height = img.size
    raw = img.tobytes("raw", "BGRA")

    cfb = bytearray((width * height) // 2)

    index = 0
    for i in range(0, len(raw), 4):
        b = raw[i + 0]
        g = raw[i + 1]
        r = raw[i + 2]
        a = raw[i + 3]
        r = (r * a) // 255
        g = (g * a) // 255
        b = (b * a) // 255

        rgb = (r << 16) | (g << 8) | b

        if rgb == 0x000000:
            color = 0      # BLACK
        elif rgb == 0xFFFF00:
            color = 2      # YELLOW
        elif rgb == 0xFF0000:
            color = 3      # RED
        elif rgb == 0x0000FF:
            color = 5      # BLUE
        elif rgb == 0x00FF00:
            color = 6      # GREEN
        else:
            color = 1      # WHITE (default)

        if index & 1:
            cfb[index >> 1] |= color
        else:
            cfb[index >> 1] |= (color << 4)

        index += 1
        if index >= width * height:
            break

    if output_image:
        with open(output_image, "wb") as f:
            f.write(cfb)
            f.flush()
            os.fsync(f.fileno())

    dither_png.unlink(missing_ok=True)

def make_encrypted_image(image_id, s6_image_file_path, public_key, cbc_iv, x_offset, y_offset, width, height, caption, orientation):

    aes_enc_key = os.urandom(32)
    sha256_hash = 0
    image_data = b""
    with open(s6_image_file_path, "rb") as f:
        image_data = f.read()
        sha256_hash = hashlib.sha256(image_data).digest()

    enc_blk3_bin = encrypt_aes_cbc(aes_enc_key, cbc_iv, image_data)

    block2_bin = b""
    block2_bin += aes_enc_key

    block2_bin += sha256_hash

    block2_bin += struct.pack("<HHHH", x_offset, y_offset, width, height)
    block2_bin += caption.encode("ascii").ljust(64, b'\x00')

    # Orientation
    block2_bin += bytes([orientation])
    rsa_encrypted_blk2 = public_key.encrypt(block2_bin, asym_padding.PKCS1v15())
    enc_image_bin = b""
    enc_image_bin += DATA_TYPE.encode("ascii")

    # Image Id, 32bit little endian
    enc_image_bin += struct.pack("<I", image_id)
    enc_image_bin += rsa_encrypted_blk2
    enc_image_bin += enc_blk3_bin
    return enc_image_bin

def crc32_from_bin(bin):
    return zlib.crc32(bin) & 0xFFFFFFFF

def crc32_from_file(filepath):
    crc = 0
    with open(filepath, 'rb') as f:
        while chunk := f.read(4096):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF
