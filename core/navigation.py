import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import logger, random_delay
from utils.selectors import DISCUSSION_TAB_SELECTOR
class Navigator:
    def __init__(self, driver):
        self.driver = driver
        self.selector_memory = {}
        self.performance_metrics = {"total_finds": 0, "total_time": 0.0}

    def _get_optimized_selectors(self, selectors_list, memory_key=None):
        """Returns selectors sorted dynamically by historical success strikes to instantly fast-track successful pipelines."""
        if memory_key is None or not isinstance(selectors_list[0], dict):
            return selectors_list
            
        if memory_key not in self.selector_memory:
            self.selector_memory[memory_key] = [{"config": sel, "hits": 0, "last_used": False} for sel in selectors_list]
            
        state = self.selector_memory[memory_key]
        state.sort(key=lambda x: (x["last_used"], x["hits"]), reverse=True)
        return [item["config"] for item in state]
        
    def _record_success(self, memory_key, successful_selector, resolution_time, fallbacks_used):
        if memory_key in self.selector_memory:
            for item in self.selector_memory[memory_key]:
                if item["config"] == successful_selector:
                    item["hits"] += 1
                    item["last_used"] = True
                else:
                    item["last_used"] = False
                    
        self.performance_metrics["total_finds"] += 1
        self.performance_metrics["total_time"] += resolution_time
        avg_time = self.performance_metrics["total_time"] / self.performance_metrics["total_finds"]
        
        logger.success(f"[METRIC] Found in {resolution_time:.2f}s | Fallbacks: {fallbacks_used} | Avg: {avg_time:.2f}s")

    def _fast_poll_elements(self, optimized_list, require_interactable=False, global_timeout=4.0):
        """
        PARALLEL CHECK LOGIC: 
        Disables Appium implicit waits, instantly looping through all selectors against the DOM 
        without blocking. Returns the absolute fastest resolution under the global cap.
        """
        self.driver.implicitly_wait(0)
        start_time = time.time()
        
        fallbacks_used = 0
        
        while time.time() - start_time < global_timeout:
            for i, selector in enumerate(optimized_list):
                by = selector["by"]
                value = selector["value"]
                
                try:
                    elements = self.driver.find_elements(by, value)
                    if elements:
                        element = elements[0]
                        if require_interactable:
                            if element.is_displayed() and element.is_enabled():
                                self.driver.implicitly_wait(10)
                                return element, selector, (time.time() - start_time), i
                        else:
                            self.driver.implicitly_wait(10)
                            return element, selector, (time.time() - start_time), i
                except Exception:
                    pass
            
            time.sleep(0.5)
            fallbacks_used += len(optimized_list)
            
        self.driver.implicitly_wait(10)
        return None, None, (time.time() - start_time), fallbacks_used

    def safe_find(self, selectors_list, global_timeout=5.0, retries=1, **kwargs):
        """Non-blocking parallel DOM polling to resolve UI elements instantly."""
        memory_key = selectors_list[0].get("value") if isinstance(selectors_list[0], dict) else str(selectors_list)
        optimized_list = self._get_optimized_selectors(selectors_list, memory_key)
        
        for attempt in range(retries):
            element, winning_selector, resolution_time, fallbacks = self._fast_poll_elements(optimized_list, require_interactable=False, global_timeout=global_timeout)
            
            if element:
                self._record_success(memory_key, winning_selector, resolution_time, fallbacks)
                return element
                
        logger.warning(f"Element not found, skipping. ({memory_key})")
        return None

    def safe_click(self, selectors_list, global_timeout=5.0, retries=1, **kwargs):
        """Fast-fail resolution and interaction."""
        memory_key = selectors_list[0].get("value") if isinstance(selectors_list[0], dict) else str(selectors_list)
        optimized_list = self._get_optimized_selectors(selectors_list, memory_key)
        
        for attempt in range(retries):
            element, winning_selector, resolution_time, fallbacks = self._fast_poll_elements(optimized_list, require_interactable=True, global_timeout=global_timeout)
            
            if element:
                try:
                    element.click()
                    self._record_success(memory_key, winning_selector, resolution_time, fallbacks)
                    return True
                except Exception as e:
                    logger.debug(f"Click exception: {e}")
                    
        logger.warning(f"Element not found, skipping click. ({memory_key})")
        return False

    def safe_type(self, selectors_list, text, global_timeout=5.0, retries=1, **kwargs):
        """Instantly locates and injects payloads via unblocked queries."""
        memory_key = selectors_list[0].get("value") if isinstance(selectors_list[0], dict) else str(selectors_list)
        optimized_list = self._get_optimized_selectors(selectors_list, memory_key)
        
        for attempt in range(retries):
            element, winning_selector, resolution_time, fallbacks = self._fast_poll_elements(optimized_list, require_interactable=True, global_timeout=global_timeout)
            
            if element:
                try:
                    element.click()
                    random_delay(0.5, 1.0)
                    element.clear()
                    element.send_keys(text)
                    
                    entered = element.text
                    if text.strip() in entered.strip() or len(entered) > 0:
                        self._record_success(memory_key, winning_selector, resolution_time, fallbacks)
                        return True
                except Exception as e:
                    logger.debug(f"Type exception: {e}")
                    
        logger.warning(f"Element not found, skipping type. ({memory_key})")
        return False

    def select_eligible_match(self, filters):
        """Locates and enters a professional match based on sport and league exclusion criteria."""
        allowed_sports = filters.get("allowed_sports", [])
        exclude_keywords = [k.lower() for k in filters.get("exclude_keywords", [])]
        
        from utils.selectors import SPORT_CATEGORY_ICON, MATCH_LIST_ITEM
        
        self.driver.implicitly_wait(0)
        size = self.driver.get_window_size()
        
        for sport in allowed_sports:
            # Fallback for Football -> Soccer
            sport_names = [sport]
            if sport == "Football": sport_names.append("Soccer")
            
            success = False
            for name in sport_names:
                logger.info(f"Checking for eligible {name} matches...")
                sport_selector = [{"by": s["by"], "value": s["value"].format(sport=name)} for s in SPORT_CATEGORY_ICON]
                success = self.safe_click(sport_selector, global_timeout=2.0)
                if success: break
            
            # If not found, attempt dynamic swipes
            if not success:
                for swipe_attempt in range(3):
                    logger.info(f"{sport} not visible. Swiping category bar (Attempt {swipe_attempt+1})...")
                    # Swipe the top 20% of the screen
                    self.driver.swipe(size['width']*0.9, size['height']*0.15, size['width']*0.1, size['height']*0.15, 600)
                    time.sleep(1)
                    for name in sport_names:
                        sport_selector = [{"by": s["by"], "value": s["value"].format(sport=name)} for s in SPORT_CATEGORY_ICON]
                        success = self.safe_click(sport_selector, global_timeout=1.5)
                        if success: break
                    if success: break
            
            if not success:
                logger.warning(f"Could not locate {sport} category icon after swiping.")
                continue
                
            random_delay(2, 4)
            
            matches = self.driver.find_elements(MATCH_LIST_ITEM[0]["by"], MATCH_LIST_ITEM[0]["value"])
            logger.info(f"Found {len(matches)} total matches in {sport} list. Evaluating eligibility...")
            
            if not matches:
                continue
                
            for match in matches:
                try:
                    match_info = str(match.get_attribute("content-desc") or "").lower()
                    match_text = str(match.text or "").lower()
                    
                    found_keyword = None
                    for word in exclude_keywords:
                        if word in match_info or word in match_text:
                            found_keyword = word
                            break
                    
                    if not found_keyword:
                        logger.success(f"ENTERING PROFESSIONAL MATCH: {match_text[:40]}")
                        match.click()
                        random_delay(3, 5)
                        self.driver.implicitly_wait(10)
                        return True
                    else:
                        logger.warning(f"Skipping: contains '{found_keyword}'")
                except Exception as e:
                    continue
        
        self.driver.implicitly_wait(10)
        logger.error("No eligible professional matches found in any allowed category.")
        return False

    def navigate_to_discussion_tab(self):
        logger.trace("Navigating to Discussion Tab...")
        success = self.safe_click(DISCUSSION_TAB_SELECTOR, global_timeout=4.0)
        if success:
            random_delay(2, 4)
            return True
        return False

