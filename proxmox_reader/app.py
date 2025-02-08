import time
import logging
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Configuration from .env file
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
TOKEN_ID = os.getenv("TOKEN_ID")
TOKEN_SECRET = os.getenv("TOKEN_SECRET")
NODE_NAME = os.getenv("NODE_NAME")
VM_ID = os.getenv("VM_ID")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")

headers = {
    'Authorization': 'PVEAPItoken=root@pam!%s=%s' % (TOKEN_ID, TOKEN_SECRET)
}

# Setup logging
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def dump_vm_configuration():
    try:
        # Get VM configuration
        response = requests.get(
            f"http://{PROXMOX_HOST}/api2/json/nodes/", 
            headers=headers,
            verify=False
        )
        response.raise_for_status()
        vm_config = response.json()['data']

        # Dump VM configuration to log file
        logging.info("VM configuration: %s", str(vm_config))

    except Exception as e:
        logging.error("Error dumping VM configuration: %s", str(e))

# Run the script every hour
if __name__ == "__main__":
    while True:
        dump_vm_configuration()
        time.sleep(3600)  # Wait for 1 hour (3600 seconds)
