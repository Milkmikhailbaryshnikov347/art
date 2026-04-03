import sys
import os
import base64
import json
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import epd_util

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 device_register.py <device_id>")
        sys.exit(1)

    try:
        art_sdk_root = os.getcwd()
        device_id = sys.argv[1]
        api_url = f"http://smartwiz-art-{device_id}.local/api/control/request"

        # Generate app private/public key pair if not exist
        private_key_path = f"{art_sdk_root}/app_private.der"
        if not os.path.exists(private_key_path):
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            private_der = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            with open(f"{art_sdk_root}/app_private.der", "wb") as f:
                f.write(private_der)

            public_key = private_key.public_key()
            public_der = public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo)

            with open(f"{art_sdk_root}/app_public.der", "wb") as f:
                f.write(public_der)

        app_private_key = None
        with open(private_key_path, "rb") as f:
            app_private_key = load_der_private_key(f.read(), password=None)

        app_public_key = None
        app_public_key_file_path = f"{art_sdk_root}/app_public.der"
        with open(app_public_key_file_path, "rb") as binary_file:
            app_public_key = binary_file.read()

        request_id  = str(1) # Fixed request_id to 1
        request_utc = epd_util.get_current_request_utc()
        response = epd_util.send_device_register_request(api_url, request_id, request_utc, app_private_key, app_public_key)
        if response is None:
            print("device_register_request failed")
            sys.exit(1)

        json_resp = response.json()
        base64_epd_public_key = json_resp["public_key"]
        epd_public_key_bin = base64.b64decode(base64_epd_public_key)
        epd_public_key_file_path = f"{art_sdk_root}/epd_public_key.der"
        with open(epd_public_key_file_path, "wb") as f:
            f.write(epd_public_key_bin)

        sys.exit(0)
    except Exception as e:
        print(f"Device register failed: {e}")
        sys.exit(1)
