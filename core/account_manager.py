import json
import os
import time
from utils.helpers import logger

class AccountManager:
    def __init__(self, config=None, accounts_file="accounts/accounts.json"):
        self.accounts_file = accounts_file
        self._last_modified_time = 0
        self.accounts = []
        self.account_stats = {}
        self.current_index = 0
        
        if config:
            source = config.get("bot", {}).get("account_source", "file")
            if source == "telegram":
                tg_config = config.get("telegram", {})
                logger.info("Telegram account sync enabled. Polling for remote credentials...")
                try:
                    from core.telegram_account_loader import TelegramAccountLoader
                    loader = TelegramAccountLoader(
                        bot_token=tg_config.get("bot_token", ""),
                        channel_id=tg_config.get("channel_id", "")
                    )
                    loader.sync_accounts(self.accounts_file)
                except Exception as e:
                    logger.warning("Telegram module failure. Proceeding with local file.")
                    
        self.load_accounts()

    def _check_for_updates(self):
        if not os.path.exists(self.accounts_file):
            return
            
        current_mtime = os.path.getmtime(self.accounts_file)
        if current_mtime > self._last_modified_time:
            if self._last_modified_time != 0:
                logger.info("Accounts file updated, reloading...")
            self._last_modified_time = current_mtime
            self.load_accounts(reload=True)

    def load_accounts(self, reload=False):
        if not os.path.exists(self.accounts_file):
            logger.error(f"Accounts file not found: {self.accounts_file}")
            return []
        try:
            with open(self.accounts_file, 'r') as f:
                new_accounts = json.load(f)
                
            new_stats = {}
            for acc in new_accounts:
                username = acc["username"]
                if username in self.account_stats:
                    new_stats[username] = self.account_stats[username]
                    if self.account_stats[username]["status"] != "disabled" and self.account_stats[username].get("disabled_until", 0) == 0:
                        new_stats[username]["status"] = acc.get("status", "active")
                else:
                    new_stats[username] = {
                        "comments_posted": 0, 
                        "status": acc.get("status", "active"), 
                        "timestamps": [],
                        "failures": 0,
                        "disabled_until": 0
                    }
                    
            self.accounts = new_accounts
            self.account_stats = new_stats
            
            if not reload:
                logger.info(f"Loaded {len(self.accounts)} accounts.")
                
            return self.accounts
        except Exception as e:
            logger.exception(f"Failed to load accounts: {e}")
            return self.accounts

    def get_active_accounts(self):
        self._check_for_updates()
        active = []
        now = time.time()
        for acc in self.accounts:
            username = acc["username"]
            stats = self.account_stats[username]
            
            if stats["status"] == "disabled" and stats.get("disabled_until", 0) > 0:
                if now >= stats["disabled_until"]:
                    stats["status"] = "active"
                    stats["failures"] = 0
                    stats["disabled_until"] = 0
                    logger.info(f"Account {username} restored")
            
            if stats["status"] == "active":
                active.append(acc)
                
        return active

    def rotate_accounts(self):
        self._check_for_updates()
        active = self.get_active_accounts()
        if not active:
            return None
        account = active[self.current_index % len(active)]
        self.current_index += 1
        return account

    def mark_usage(self, username):
        if username in self.account_stats:
            self.account_stats[username]["comments_posted"] += 1
            self.account_stats[username].setdefault("timestamps", []).append(time.time())
            
    def record_failure(self, username):
        if username in self.account_stats:
            stats = self.account_stats[username]
            stats["failures"] = stats.get("failures", 0) + 1
            
            if stats["failures"] >= 3:
                import random
                stats["status"] = "disabled"
                cooldown_seconds = random.randint(600, 1800)
                stats["disabled_until"] = time.time() + cooldown_seconds
                logger.error(f"Account {username} temporarily disabled")

    def disable_account(self, username):
        if username in self.account_stats:
            self.account_stats[username]["status"] = "disabled"
            self.account_stats[username]["disabled_until"] = 0
            logger.error(f"Account disabled: {username}")
            
    def get_comments_count(self, username):
        return self.account_stats.get(username, {}).get("comments_posted", 0)

    def get_comments_count_last_hour(self, username):
        if username not in self.account_stats:
            return 0
        timestamps = self.account_stats[username].setdefault("timestamps", [])
        now = time.time()
        valid = [t for t in timestamps if now - t <= 3600]
        self.account_stats[username]["timestamps"] = valid
        return len(valid)

