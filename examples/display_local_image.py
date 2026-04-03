#import pytest
import sys
import os
import epd_util
import json
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives import serialization

def on_custom_data_receive(data):
    global response
    response = data.decode('utf-8')

if __name__ == "__main__":

    try:
        if len(sys.argv) < 3:
            print(f"Usage: python3 display_local_image.py <device_id> <image_file.s6>")
            sys.exit(1)

        device_id = sys.argv[1]
        s6_image_file_path = sys.argv[2]

        private_key_path = f"{os.getcwd()}/app_private.der"
        if not os.path.exists(private_key_path):
            print("app_private.der not found")
            sys.exit(-1)

        app_private_key = None
        with open(private_key_path, "rb") as f:
            app_private_key = load_der_private_key(f.read(), password=None)

        api_url = f"http://smartwiz-art-{device_id}.local/api/control/request"

        # Fixed request_id to 1
        request_id = str(1)
        request_utc = epd_util.get_current_request_utc()

        epd_public_key_file_path = f"{os.getcwd()}/epd_public_key.der"
        epd_public_key =None
        with open(epd_public_key_file_path, "rb") as f:
            epd_public_key_bin = f.read()

        cbc_iv = device_id[16:].encode('ascii')
        caption = "Test Rainbow Image!"
        orientation = 0

        x_offset = 0
        y_offset = 0
        witdh = 800
        height = 480
        epd_public_key = serialization.load_der_public_key(epd_public_key_bin)
        encrypted_image = epd_util.make_encrypted_image(0, s6_image_file_path, epd_public_key, cbc_iv, x_offset, y_offset, witdh, height, caption, orientation)

        request_utc = epd_util.get_current_request_utc()
        response = epd_util.send_image_upload_request(api_url, request_id, request_utc, app_private_key, encrypted_image)
        json_resp = response.json()
        print(json_resp)

        file = json_resp["file"]

        request_utc = epd_util.get_current_request_utc()
        user_name   = "smartwizart-cli-user"
        user_comment = "user image by smartwizart-cli"
        response = epd_util.send_display_request(api_url, request_id, request_utc, app_private_key, file, user_name, user_comment)
        json_resp = response.json()
        print(json_resp)
        sys.exit(0)
    except Exception as e:
        print(f"Display local image failed: {e}")
        sys.exit(1)
