import os
from pathlib import Path
import shutil
import sys
import requests
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives import serialization

art_sdk_root = os.getenv("ART_SDK_ROOT")
if art_sdk_root is None:
    print(f"Error: ART_SDK_ROOT is not set. Please run '. ./export.sh' in the `examples` directory.", file=sys.stderr)
    sys.exit(1)

sys.path.append(art_sdk_root)
import epd_util

def get_camera_snapshot_from_ha(access_token, camera_entity_id):
    """Retrieve camera snapshot from Home Assistant."""
    url = f"http://homeassistant.local:8123/api/camera_proxy/{camera_entity_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        with open("snapshot.jpg", "wb") as f:
            f.write(response.content)
        return Path("snapshot.jpg")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching camera snapshot: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 display_camera_snapshot.py <device_id> <camera_entity_id>")
        sys.exit(1)

    if not shutil.which("convert"):
        print("convert not found. Please install imagemagick.")
        sys.exit(1)

    access_token = os.getenv("HA_ACCESS_TOKEN")
    if access_token is None:
        print(f"HA_ACCESS_TOKEN is not set. Please export HA_ACCESS_TOKEN environment variable with your Home Assistant long-lived access token.", file=sys.stderr)
        sys.exit(1)

    try:
        device_id = sys.argv[1]
        camera_entity_id = sys.argv[2]
        snapshot_url = f"http://homeassistant.local:8123/api/camera_proxy/{camera_entity_id}"
        input_image = get_camera_snapshot_from_ha(access_token, camera_entity_id)
        if input_image is None:
            print("Failed to download snapshot image.")
            sys.exit(1)

        s6_image = Path("snapshot.s6")
        epd_util.convert_image_to_s6(input_image, s6_image)

        private_key_path = f"{art_sdk_root}/app_private.der"
        if not os.path.exists(private_key_path):
            print("app_private.der not found")
            sys.exit(-1)

        app_private_key = None
        with open(private_key_path, "rb") as f:
            app_private_key = load_der_private_key(f.read(), password=None)

        api_url = f"http://smartwiz-art-{device_id}.local/api/control/request"

        request_id = str(1)  # Fixed request_id to 1
        request_utc = epd_util.get_current_request_utc()

        epd_public_key_file_path = f"{art_sdk_root}/epd_public_key.der"
        epd_public_key =None
        with open(epd_public_key_file_path, "rb") as f:
            epd_public_key_bin = f.read()

        cbc_iv = device_id[16:].encode('ascii')
        caption = ""
        orientation = 0

        # encrypt image
        x_offset = 0
        y_offset = 0
        witdh = 800
        height = 480
        epd_public_key = serialization.load_der_public_key(epd_public_key_bin)
        encrypted_image = epd_util.make_encrypted_image(0, s6_image, epd_public_key, cbc_iv, x_offset, y_offset, witdh, height, caption, orientation)

        # =====================================================
        # upload image
        # =====================================================
        request_id = str(1)  # Fixed request_id to 1
        request_utc = epd_util.get_current_request_utc()
        response = epd_util.send_image_upload_request(api_url, request_id, request_utc, app_private_key, encrypted_image)
        json_resp = response.json()
        print(json_resp)
        file = json_resp["file"]

        input_image.unlink(missing_ok=True)
        s6_image.unlink(missing_ok=True)

        # =====================================================
        # display image request
        # =====================================================
        request_utc = epd_util.get_current_request_utc()
        user_name   = "smartwizart-cli-user"
        user_comment = "user image by smartwizart-cli"
        response = epd_util.send_display_request(api_url, request_id, request_utc, app_private_key, file, user_name, user_comment)
        json_resp = response.json()
        print(json_resp)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    