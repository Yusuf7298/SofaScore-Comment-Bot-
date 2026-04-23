import time
import random
from utils.helpers import logger, random_delay
from core.account_manager import AccountManager
from core.session_manager import SessionManager
from core.navigation import Navigator
from core.actions import CommentActions
from core.detector import MatchEventDetector

class Scheduler:
    def __init__(self, config):
        self.config = config
        self.account_manager = AccountManager(config=self.config)
        self.session_manager = SessionManager()
        
    def run_sequential(self):
        """Runs accounts one after another in a loop"""
        bot_settings = self.config.get("bot", {})
        anti_ban = self.config.get("anti_ban", {})
        
        active_accounts = self.account_manager.get_active_accounts()
        if not active_accounts:
            logger.error("No active accounts available to run.")
            return
            
        logger.info(f"Starting execution pool.")
        
        while True:
            account = self.account_manager.rotate_accounts()
            if not account:
                logger.warning("All accounts have failed or hit limits. Stopping scheduler.")
                break
                
            username = account["username"]
                
            max_per_account = bot_settings.get("max_comments", 5)
            if self.account_manager.get_comments_count(username) >= max_per_account:
                logger.info(f"[{username}] Reached max comments limit ({max_per_account}). Marking failed/done.")
                self.account_manager.disable_account(username)
                continue
                
            max_per_hour = bot_settings.get("max_comments_per_hour", 3)
            if self.account_manager.get_comments_count_last_hour(username) >= max_per_hour:
                logger.warning(f"[{username}] Account skipped (Reached hourly limits)")
                continue
                
            logger.info(f"Running account: {username}")
            driver = self.session_manager.start_session(account)
            
            if not driver:
                logger.warning(f"[{username}] Driver failed to start. Recording failure.")
                self.account_manager.record_failure(username)
                continue
                
            try:
                self._run_account_cycle(username, driver, account)
            except Exception as e:
                logger.exception(f"[{username}] Encountered fatal error during cycle: {e}")
                logger.warning(f"[{username}] Session crashed. Recording failure.")
                self.account_manager.record_failure(username)
            finally:
                self.session_manager.close_session(username)
                
            rest_delay = anti_ban.get("account_switch_delay_seconds", 15)
            logger.info(f"Resting for {rest_delay}s before next account...")
            time.sleep(rest_delay)

    def _run_account_cycle(self, username, driver, account):
        """The actual commenting cycle for a single account session - Now with Sport Rotation"""
        navigator = Navigator(driver)
        actions = CommentActions(driver, navigator)
        bot_settings = self.config.get("bot", {})
        available_comments = list(self.config.get("comments", []))
        dry_run_enabled = bot_settings.get("dry_run", False)
        anti_ban = self.config.get("anti_ban", {})
        
        random_delay(anti_ban.get("min_delay_sec", 3), anti_ban.get("max_delay_sec", 10))
        
        # MULTI-SPORT CYCLE
        allowed_sports = self.config.get("match_filters", {}).get("allowed_sports", ["Football"])
        comments_posted_session = 0
        max_total = bot_settings.get("max_comments", 5)
        
        for sport in allowed_sports:
            if comments_posted_session >= max_total:
                logger.info(f"[{username}] Reached session limit ({max_total}).")
                break
                
            logger.info(f"[{username}] Starting cycle for sport: {sport}")
            
            # 1. SELECT MATCH FOR THIS SPORT
            match_filters = self.config.get("match_filters", {}).copy()
            match_filters["allowed_sports"] = [sport]
            
            if not navigator.select_eligible_match(match_filters):
                logger.warning(f"[{username}] No matches available for {sport}. Switching to next sport.")
                continue
            
            # 2. NAVIGATE & POST
            if not navigator.navigate_to_discussion_tab():
                logger.error(f"[{username}] Could not open discussion for {sport}.")
                continue
                
            actions.simulate_human_behavior()
            
            # 3. POST IMMEDIATELY (Eager Posting)
            if not available_comments:
                logger.warning(f"[{username}] Out of unique comments.")
                break
                
            selected_comment = random.choice(available_comments)
            available_comments.remove(selected_comment)
            
            success = actions.post_comment(selected_comment, dry_run=dry_run_enabled)
            
            if success:
                comments_posted_session += 1
                self.account_manager.mark_usage(username)
                cooldown = bot_settings.get("cooldown_between_comments_seconds", 15)
                logger.success(f"[{username}] Posted successfully in {sport}! Waiting {cooldown}s before next sport...")
                time.sleep(cooldown)
            else:
                logger.error(f"[{username}] Post failed in {sport}.")
                self.account_manager.record_failure(username)
            
            # The next loop's 'select_eligible_match' handles backing out to home
            
        logger.info(f"[{username}] Account cycle finished.")
