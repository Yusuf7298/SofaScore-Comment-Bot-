from appium.webdriver.common.appiumby import AppiumBy

"""
Selectors for Sofascore UI components using Adaptive Priority Structures.
"""

SCORE_TEXT = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/score_text", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/match_score", "timeout": 1.0},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().resourceIdMatches(".*score.*")', "timeout": 1.0},
    {"by": AppiumBy.XPATH, "value": "//*[contains(@resource-id, 'score') or contains(@resource-id, 'result')]", "timeout": 0.5}
]

MATCH_TIME_TEXT = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/time_text", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/match_time", "timeout": 1.0},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().resourceIdMatches(".*time.*")', "timeout": 1.0},
    {"by": AppiumBy.XPATH, "value": "//*[contains(@resource-id, 'time')]", "timeout": 0.5}
]

DISCUSSION_TAB_SELECTOR = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/multiStateFab", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/multi_state_fab", "timeout": 1.0},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Chat", "timeout": 0.5},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Comments", "timeout": 0.5},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Discussion", "timeout": 0.5},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().className("com.google.android.material.floatingactionbutton.FloatingActionButton")', "timeout": 0.5},
    {"by": AppiumBy.CLASS_NAME, "value": "com.google.android.material.floatingactionbutton.FloatingActionButton", "timeout": 0.5},
    {"by": AppiumBy.XPATH, "value": "//*[contains(@resource-id, 'fab') or contains(@resource-id, 'chat') or contains(@resource-id, 'comment_button')]", "timeout": 0.5}
]

COMMENT_INPUT_BOX = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/comment_input", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/input", "timeout": 1.0},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().className("android.widget.EditText")', "timeout": 0.5},
    {"by": AppiumBy.XPATH, "value": "//android.widget.EditText", "timeout": 0.5}
]

POST_COMMENT_BUTTON = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/button_send_comment", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/send", "timeout": 1.0},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Send", "timeout": 0.5},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().descriptionMatches("(?i)send")', "timeout": 0.5},
    {"by": AppiumBy.XPATH, "value": "//*[@content-desc='Send' or @text='Send']", "timeout": 0.5}
]
