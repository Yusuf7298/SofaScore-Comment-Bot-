from appium.webdriver.common.appiumby import AppiumBy


SCORE_TEXT = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/score_text", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/match_score", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/score", "timeout": 1.0},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().resourceIdMatches(".*score.*")', "timeout": 1.0}
]

MATCH_TIME_TEXT = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/time_text", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/match_time", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/status", "timeout": 1.0},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().resourceIdMatches(".*time|status.*")', "timeout": 1.0}
]

DISCUSSION_TAB_SELECTOR = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/multiStateFab", "timeout": 2.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/multi_state_fab", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/button_join_discussion", "timeout": 1.0},
    {"by": AppiumBy.XPATH, "value": "//*[@text='CHAT' or @text='Chat' or @text='DISCUSSION' or @text='Comments' or contains(@text, 'SOCIAL') or contains(@text, 'JOIN')]", "timeout": 1.0},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Chat", "timeout": 0.5},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Comments", "timeout": 0.5},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Discussion", "timeout": 0.5},
    {"by": AppiumBy.ANDROID_UIAUTOMATOR, "value": 'new UiSelector().textMatches("(?i)chat|discussion|comments|social|join")', "timeout": 0.5}
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
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/button_send", "timeout": 1.0},
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/send_button", "timeout": 1.0},
    {"by": AppiumBy.XPATH, "value": "//android.widget.EditText/following-sibling::android.widget.ImageView", "timeout": 1.0},
    {"by": AppiumBy.XPATH, "value": "//android.widget.EditText/parent::*//android.widget.ImageView[@clickable='true']", "timeout": 1.0},
    {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Send", "timeout": 0.5},
    {"by": AppiumBy.XPATH, "value": "//*[contains(@resource-id, 'send') or @content-desc='Send' or @text='Send']", "timeout": 0.5}
]

MATCH_LIST_ITEM = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/match_cell", "timeout": 1.0},
    {"by": AppiumBy.XPATH, "value": "//android.view.ViewGroup[contains(@resource-id, 'match_cell')]", "timeout": 0.5}
]

LEAGUE_HEADER = [
    {"by": AppiumBy.ID, "value": "com.sofascore.results:id/header_text", "timeout": 1.0},
    {"by": AppiumBy.XPATH, "value": "//*[contains(@resource-id, 'tournament') or contains(@resource-id, 'league')]", "timeout": 0.5}
]

SPORT_CATEGORY_ICON = [
    {"by": AppiumBy.XPATH, "value": "//*[@text='{sport}' or contains(@content-desc, '{sport}') or contains(@text, '{sport}')]", "timeout": 1.0}
]
