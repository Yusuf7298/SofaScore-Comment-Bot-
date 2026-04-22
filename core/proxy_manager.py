import subprocess
import time
from utils.helpers import logger
import os

class ProxyManager:
    """
    Manages setting and clearing proxies via ADB.
    Note: Android requires ADB global HTTP proxy for non-rooted devices without third-party apps.
    This may not work for SOCKS5 or proxies requiring username/password authentication natively.
    """
    def __init__(self, adb_path=None):
        self.adb_path = adb_path or os.environ.get("LOCALAPPDATA", "") + r"\Android\Sdk\platform-tools\adb.exe"

    def set_proxy(self, udid, proxy_string):
        """Sets the global HTTP proxy for the specific device."""
        if not proxy_string:
            logger.info("No proxy provided, skipping proxy setup.")
            return True

        proxy_val = proxy_string.replace("http://", "").replace("https://", "")
        logger.info(f"Setting proxy {proxy_val} for device {udid}...")
        
        try:
            cmd = f'"{self.adb_path}" -s {udid} shell settings put global http_proxy {proxy_val}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to set proxy via ADB. Stderr: {result.stderr}")
                return False
                
            logger.info(f"Proxy successfully set to {proxy_val} for {udid}.")
            time.sleep(2)
            return True
        except Exception as e:
            logger.exception(f"Error executing ADB proxy command: {e}")
            return False

    def clear_proxy(self, udid):
        """Clears the global HTTP proxy for the specific device."""
        logger.info(f"Clearing proxy for device {udid}...")
        try:
            cmd = f'"{self.adb_path}" -s {udid} shell settings put global http_proxy :0'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Failed to clear proxy via ADB. Stderr: {result.stderr}")
                return False
            logger.info(f"Proxy successfully cleared for {udid}.")
            return True
        except Exception as e:
            logger.exception(f"Error executing ADB proxy clear command: {e}")
            return False

