import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.helpers import logger, random_delay
from utils.selectors import COMMENT_INPUT_BOX, POST_COMMENT_BUTTON, DISCUSSION_TAB_SELECTOR
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

class CommentActions:
    def __init__(self, driver, navigator):
        self.driver = driver
        self.navigator = navigator

    def simulate_human_behavior(self):
        """Simulates random swiping/scrolling and reading pauses to avoid bot detection."""
        logger.trace("Simulating human behavior...")
        try:
            window_size = self.driver.get_window_size()
            width, height = window_size['width'], window_size['height']
            scroll_type = random.choice(["down", "up", "idle"])
            
            if scroll_type == "idle":
                random_delay(1, 2)
                return
                
            start_x = int(width / 2)
            start_y = int(height * 0.8) if scroll_type == "down" else int(height * 0.2)
            end_y = int(height * 0.2) if scroll_type == "down" else int(height * 0.8)
                
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(start_x, end_y)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            random_delay(0.5, 1.5)
        except Exception as e:
            logger.debug(f"Scroll simulation failed: {e}")

    def post_comment(self, comment_text, dry_run=False):
        """Executes the action of posting a comment with strict performance bounds and state-machine recovery."""
        logger.info(f"Posting comment: '{comment_text}'")
        
        recovery_attempts = 0
        max_recoveries = 2
        
        while True:
            if self.navigator.safe_find(COMMENT_INPUT_BOX, global_timeout=1.0):
                break 
                
            recovery_attempts += 1
            if recovery_attempts > max_recoveries:
                logger.error("[ERROR] Recovery failed, skipping.")
                return False
                
            logger.warning("[WARNING] Recovery triggered: Input missing.")
            
            if self.navigator.safe_find(DISCUSSION_TAB_SELECTOR, global_timeout=1.0):
                logger.info("Opening discussion panel...")
                self.navigator.safe_click(DISCUSSION_TAB_SELECTOR, global_timeout=1.5)
                random_delay(1, 2)
                continue
                
            logger.error("[ERROR] Recovery failed: Unknown UI state.")
            return False
            
        time.sleep(random.uniform(1.0, 3.0))
        
        if not self.navigator.safe_type(COMMENT_INPUT_BOX, text=comment_text, global_timeout=4.0):
            logger.error("Failed to type comment. Aborting.")
            return False
            
        try:
            self.driver.hide_keyboard()
            time.sleep(0.5)
        except:
            pass
                
        if dry_run:
            logger.success("Comment simulated successfully (Dry Run).")
            return True
            
        if not self.navigator.safe_click(POST_COMMENT_BUTTON, global_timeout=3.0):
            logger.warning("Failed to click Send button. Trying Enter key backup...")
            try:
                self.driver.press_keycode(66)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Post failed: {e}")
                return False
            
        logger.trace("Verifying post...")
        posted_text_selector = [{"by": AppiumBy.XPATH, "value": f"//*[contains(@text, '{comment_text}')]"}]
        if self.navigator.safe_find(posted_text_selector, global_timeout=3.0):
            logger.success("Comment posted successfully")
            return True
            
        input_el = self.navigator.safe_find(COMMENT_INPUT_BOX, global_timeout=2.0)
        if input_el and (not input_el.text or input_el.text != comment_text):
            logger.success("Comment posted successfully (Input cleared)")
            return True
                
        logger.warning("Verification failed, but continuing flow.")
        return True

