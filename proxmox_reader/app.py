import time
import logging
from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration from .env file
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
TOKEN_NAME = os.getenv("TOKEN_NAME")
TOKEN_SECRET = os.getenv("TOKEN_SECRET")
NODE_NAME = os.getenv("NODE_NAME")
VM_ID = os.getenv("VM_ID")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")

# Setup logging
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def dump_vm_configuration():
    try:
        # Connect to Proxmox API
        proxmox = ProxmoxAPI(
            PROXMOX_HOST,
            token_name=TOKEN_NAME,
            token_secret=TOKEN_SECRET,
            verify_ssl=False  # Disable SSL verification if using self-signed certs
        )
        
        # Get VM configuration
        vm_config = proxmox.nodes(NODE_NAME).qemu(VM_ID).config.get()
        
        # Log VM configuration
        logging.info("Dumping VM Configuration for VM ID %s on Node %s", VM_ID, NODE_NAME)
        logging.info(vm_config)

    except Exception as e:
        logging.error("Error dumping VM configuration: %s", str(e))

# Run the script every hour
if __name__ == "__main__":
    while True:
        dump_vm_configuration()
        time.sleep(3600)  # Wait for 1 hour (3600 seconds)
