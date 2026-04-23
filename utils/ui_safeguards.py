import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException
from utils.helpers import logger, random_delay
class SafeUI:
    def __init__(self, driver, default_timeout=15):
        self.driver = driver
        self.default_timeout = default_timeout
    def safe_find(self, selector_chain, timeout=None, retries=3):
        wait_time = timeout if timeout else self.default_timeout
        wait = WebDriverWait(self.driver, wait_time, ignored_exceptions=[StaleElementReferenceException])
        
        for attempt in range(retries):
            for strategy, locator in selector_chain:
                try:
                    logger.trace(f"Attempting find via {strategy}: {locator}")
                    element = wait.until(EC.presence_of_element_located((strategy, locator)))
                    if element:
                        logger.success(f"Element found using {strategy}: {locator}")
                        return element
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Locator {locator} failed: {e}")
                    continue
            logger.warning(f"Failed to find element after attempt {attempt + 1}/{retries}. Retrying...")
            time.sleep(2)
        logger.error(f"Could not locate element after all {retries} retries using chain: {selector_chain}")
        return None
    def safe_click(self, selector_chain, timeout=None, retries=3):
        wait_time = timeout if timeout else self.default_timeout
        wait = WebDriverWait(self.driver, wait_time, ignored_exceptions=[StaleElementReferenceException])
        
        for attempt in range(retries):
            for strategy, locator in selector_chain:
                try:
                    logger.trace(f"Attempting click via {strategy}: {locator}")
                    element = wait.until(EC.element_to_be_clickable((strategy, locator)))
                    if element:
                        element.click()
                        logger.success(f"Successfully clicked element via {strategy}: {locator}")
                        return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Click failed for {locator}: {e}")
                    continue
            logger.warning(f"Failed to click element after attempt {attempt + 1}/{retries}. Retrying...")
            time.sleep(2)
            
        logger.error(f"Could not click element after all {retries} retries using chain: {selector_chain}")
        return False
    def safe_send_keys(self, selector_chain, text, timeout=None, retries=3):
        wait_time = timeout if timeout else self.default_timeout
        wait = WebDriverWait(self.driver, wait_time, ignored_exceptions=[StaleElementReferenceException])
        
        for attempt in range(retries):
            for strategy, locator in selector_chain:
                try:
                    logger.trace(f"Attempting send_keys via {strategy}: {locator}")
                    element = wait.until(EC.element_to_be_clickable((strategy, locator)))
                    if element:
                        element.click()
                        random_delay(1, 2)
                        element.clear()
                        element.send_keys(text)
                        
                        entered_text = element.text
                        if entered_text and text.strip() in entered_text.strip() or len(entered_text) > 0:
                            logger.success(f"Successfully sent keys using {strategy}: {locator}")
                            return True
                        else:
                            logger.warning(f"Sent keys but text mismatch for {locator}. Retrying.")
                            continue
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Send keys failed for {locator}: {e}")
                    continue
                    
            logger.warning(f"Failed to send keys after attempt {attempt + 1}/{retries}. Retrying...")
            time.sleep(2)
            
        logger.error(f"Could not send keys after all {retries} retries using chain: {selector_chain}")
        return False