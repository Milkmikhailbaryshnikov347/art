import sys
import os
import base64
import blufi
import json
import time
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import epd_util

def on_custom_data_receive(data):
    global response
    response = data.decode('utf-8')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 device_unregister.py <device_id>")
        sys.exit(1)

    try:
        art_sdk_root = os.getcwd()
        device_id = sys.argv[1]
        api_url = f"http://smartwiz-art-{device_id}.local/api/control/request"

        private_key_path         = f"{art_sdk_root}/app_private.der"
        app_public_key_file_path = f"{art_sdk_root}/app_public.der"
        if not os.path.exists(private_key_path):
            print("app_private.der not found")
            sys.exit(-1)

        app_private_key = None
        with open(private_key_path, "rb") as f:
            app_private_key = load_der_private_key(f.read(), password=None)

        if not os.path.exists(app_public_key_file_path):
            print("app_public.der not found")
            sys.exit(-1)

        app_public_key = None
        with open(app_public_key_file_path, "rb") as binary_file:
            app_public_key = binary_file.read()

        request_id  = str(1) # Fixed request_id to 1
        request_utc = epd_util.get_current_request_utc()
        response = epd_util.send_device_unregister_request(api_url, request_id, request_utc, app_private_key)

        epd_public_key_file_path = f"{art_sdk_root}/epd_public_key.der"
        if os.path.exists(epd_public_key_file_path):
            os.remove(epd_public_key_file_path)

        sys.exit(0)
    except Exception as e:
        print(f"Device unregister failed: {e}")
        sys.exit(1)
