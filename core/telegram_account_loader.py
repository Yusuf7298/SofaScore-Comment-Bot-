import json
import os
import requests
import time
from utils.helpers import logger

class TelegramAccountLoader:
    def __init__(self, bot_token, channel_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        
    def fetch_accounts(self, retries=3):
        for attempt in range(retries):
            try:
                response = requests.get(self.api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_messages(data)
                else:
                    logger.warning(f"Telegram API returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"Telegram API request failed: {e}")
                
            time.sleep(2)
            
        logger.error("Failed to fetch accounts from Telegram after all retries. Falling back to local.")
        return []

    def _parse_messages(self, data):
        parsed_accounts = []
        try:
            results = data.get("result", [])
            for res in results:
                message = res.get("message", {}) or res.get("channel_post", {})
                text = message.get("text", "")
                
                lines = text.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    parts = line.split(":")
                    if len(parts) >= 3:
                        username = parts[0].strip()
                        password_or_udid = parts[1].strip()
                        proxy = parts[2].strip()
                        
                        parsed_accounts.append({
                            "username": username,
                            "emulator_udid": password_or_udid, 
                            "proxy": proxy,
                            "status": "active"
                        })
        except Exception as e:
            logger.error("Failed to parse Telegram message schema securely.")
            
        return parsed_accounts
        
    def sync_accounts(self, local_file_path="accounts/accounts.json"):
        remote_accounts = self.fetch_accounts()
        if not remote_accounts:
            return False
            
        local_accounts = []
        if os.path.exists(local_file_path):
            with open(local_file_path, 'r') as f:
                try:
                    local_accounts = json.load(f)
                except:
                    local_accounts = []
                
        local_usernames = {acc["username"] for acc in local_accounts}
        
        merged_count = 0
        for r_acc in remote_accounts:
            if r_acc["username"] not in local_usernames:
                local_accounts.append(r_acc)
                local_usernames.add(r_acc["username"])
                merged_count += 1
                
        if merged_count > 0:
            with open(local_file_path, 'w') as f:
                json.dump(local_accounts, f, indent=4)
            logger.info(f"Synchronized {merged_count} new accounts from Telegram into local state.")
            
        return True
