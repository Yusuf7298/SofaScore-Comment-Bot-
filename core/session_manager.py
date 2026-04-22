from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.helpers import logger
import json
import os
from core.proxy_manager import ProxyManager

class SessionManager:
    def __init__(self, config_path="config/config.json"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.proxy_manager = ProxyManager()
        self.active_sessions = {}

    def start_session(self, account):
        """Initializes the Appium driver session for a specific account/device."""
        udid = account.get("emulator_udid")
        username = account.get("username")
        proxy = account.get("proxy")

        if not udid:
            logger.error(f"Cannot start session for {username}: No emulator_udid provided.")
            return None

        if proxy:
            success = self.proxy_manager.set_proxy(udid, proxy)
            if not success:
                logger.warning(f"Failed to set proxy for {username}. Proceeding natively (Direct Network).")

        appium_config = self.config.get("appium", {})
        server_url = appium_config.get("server_url", "http://127.0.0.1:4723")
        
        logger.info(f"[{username}] Starting Appium session on device {udid}...")
        
        options = UiAutomator2Options()
        options.platform_name = appium_config.get("platformName", "Android")
        options.automation_name = appium_config.get("automationName", "UiAutomator2")
        options.app_package = appium_config.get("appPackage", "com.sofascore.results")
        options.app_activity = appium_config.get("appActivity", "com.sofascore.results.ui.main.MainActivity")
        options.no_reset = appium_config.get("noReset", True)
        options.full_reset = appium_config.get("fullReset", False)
        options.new_command_timeout = appium_config.get("newCommandTimeout", 300)
        
        options.udid = udid
        
        try:
            driver = webdriver.Remote(server_url, options=options)
            driver.implicitly_wait(10)
            
            self.active_sessions[username] = {
                "driver": driver,
                "udid": udid,
                "proxy": proxy
            }
            logger.info(f"[{username}] Connected to device successfully.")
            return driver
        except Exception as e:
            logger.exception(f"[{username}] Failed to start Appium session: {e}")
            if proxy:
                self.proxy_manager.clear_proxy(udid)
            return None

    def close_session(self, username):
        """Quits the Appium session safely and removes proxy."""
        session_info = self.active_sessions.get(username)
        if not session_info:
            return

        logger.info(f"[{username}] Closing session cleanly...")
        try:
            driver = session_info["driver"]
            if driver:
                driver.quit()
        except Exception as e:
            logger.warning(f"[{username}] Error quitting driver: {e}")
            
        udid = session_info["udid"]
        proxy = session_info["proxy"]
        if proxy:
            self.proxy_manager.clear_proxy(udid)
            
        del self.active_sessions[username]
        logger.info(f"[{username}] Session closed and device proxy reset.")
