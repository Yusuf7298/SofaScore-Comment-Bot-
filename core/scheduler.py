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
                
            rest_delay = anti_ban.get("account_switch_delay_seconds", 30)
            logger.info(f"Resting for {rest_delay}s before next account...")
            time.sleep(rest_delay)

    def _run_account_cycle(self, username, driver, account):
        """The actual commenting cycle for a single account session"""
        navigator = Navigator(driver)
        actions = CommentActions(driver, navigator)
        detector = MatchEventDetector(navigator)
        anti_ban = self.config.get("anti_ban", {})
        bot_settings = self.config.get("bot", {})
        available_comments = self.config.get("comments", [])
        dry_run_enabled = bot_settings.get("dry_run", False)
        
        random_delay(anti_ban.get("min_delay_sec", 5), anti_ban.get("max_delay_sec", 15))
        
        # 0. AUTOMATED MATCH SELECTION
        if bot_settings.get("auto_match_selection", False):
            match_filters = self.config.get("match_filters", {})
            if not navigator.select_eligible_match(match_filters):
                logger.error(f"[{username}] Could not find an eligible match. Ending cycle.")
                return
        
        logger.info(f"[{username}] Navigating to discussion tab...")
        if not navigator.navigate_to_discussion_tab():
            logger.error(f"[{username}] Failed to open discussion panel. Match might not have comments enabled.")
            return
        
        actions.simulate_human_behavior()
        
        logger.info(f"[{username}] Polling match state for an event...")
        polling_duration = bot_settings.get("polling_interval_seconds", 15)
        
        max_polls = bot_settings.get("max_polls_per_match", 3)
        comments_posted_this_match = 0
        max_per_match = bot_settings.get("max_comments_per_match", 1)
        
        for i in range(max_polls):
            if comments_posted_this_match >= max_per_match:
                logger.info(f"[{username}] Reached max comments for this match ({max_per_match}). Ending cycle.")
                break
                
            if dry_run_enabled:
                event_happened = True
            else:
                event_happened = detector.detect_change()
            
            if event_happened:
                skip_chance = anti_ban.get("skip_chance_percent", 20)
                if random.randint(1, 100) <= skip_chance:
                    logger.warning(f"[{username}] Skipped action (anti-ban)")
                    time.sleep(random.uniform(2.0, 5.0))
                    break 

                logger.info(f"[{username}] Event detected. Preparing to comment...")
                actions.simulate_human_behavior()
                
                if not available_comments:
                    logger.warning(f"[{username}] Out of unique comments to post.")
                    break
                    
                selected_comment = random.choice(available_comments)
                available_comments.remove(selected_comment)
                
                success = actions.post_comment(selected_comment, dry_run=dry_run_enabled)
                
                if success:
                    comments_posted_this_match += 1
                    self.account_manager.mark_usage(username)
                    cooldown = bot_settings.get("cooldown_between_comments_seconds", 120)
                    logger.success(f"[{username}] Comment sequence complete! Waiting {cooldown}s before tearing down session.")
                    
                    slept = 0
                    while slept < cooldown:
                        chunk = min(30, cooldown - slept)
                        time.sleep(chunk)
                        slept += chunk
                        try:
                            driver.get_window_size()
                            logger.trace(f"[{username}] Heartbeat sent to keep session alive during cooldown ({slept}/{cooldown}s)")
                        except Exception as e:
                            logger.warning(f"[{username}] Heartbeat failed, session may be unstable: {e}")
                            
                else:
                    logger.error(f"[{username}] Failed to post comment.")
                    self.account_manager.record_failure(username)
                break 
            else:
                logger.debug(f"[{username}] No event detected (Attempt {i+1}/{max_polls}). Sleeping {polling_duration}s.")
                time.sleep(polling_duration)
        
        logger.info(f"[{username}] Account cycle finished.")
