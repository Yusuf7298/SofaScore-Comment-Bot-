from utils.helpers import logger
from utils.selectors import SCORE_TEXT, MATCH_TIME_TEXT

class MatchEventDetector:
    def __init__(self, navigator):
        self.navigator = navigator
        self.last_score = None
        self.last_time = None

    def capture_current_state(self):
        """Scrapes the current match score and time from the UI."""
        from selenium.common.exceptions import StaleElementReferenceException
        score_elem = self.navigator.safe_find(SCORE_TEXT, timeout=3, retries=1)
        time_elem = self.navigator.safe_find(MATCH_TIME_TEXT, timeout=3, retries=1)
        
        current_score = None
        current_time = None
        
        try:
            if score_elem: current_score = score_elem.text
            if time_elem: current_time = time_elem.text
        except StaleElementReferenceException:
            logger.debug("Elements went stale while reading text. Polling will recover gracefully.")
            
        return current_score, current_time

    def detect_change(self):
        """
        Compares current state to previous state. 
        Returns True if a relevant 'event' happened (like a goal or significant time jump not just 1 min).
        For this MVP, we consider ANY score change to be a trigger.
        """
        current_score, current_time = self.capture_current_state()
        
        if current_score is None:
            logger.debug("Could not read score. Match might be over or UI changed.")
            return False

        logger.info(f"Current State -> Score: {current_score} | Time: {current_time}")

        if self.last_score is None:
            self.last_score = current_score
            self.last_time = current_time
            return False

        has_changed = False
        
        if current_score != self.last_score:
            logger.info(f"⚽ EVENT DETECTED! Score changed from {self.last_score} to {current_score}")
            has_changed = True
            
        self.last_score = current_score
        self.last_time = current_time
        
        return has_changed
