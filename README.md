# Sofascore Automation Bot

A production-ready, multi-account automation architecture designed to perform highly humanized interactions within the Sofascore Android application using Appium.

## Features
- **Multi-Account Orchestration**: Run multiple emulator/device profiles in a sequential, rotating loop.
- **Automated Network Proxies**: Dynamically switch Android global HTTP proxies per unique account session via ADB.
- **Human-Simulation Algorithms**: Imitate human behavior through randomized scrolling, swiping, reading delays, and dynamic wait times to bypass bot-detection algorithms.
- **Fail-Safe Processing**: Transient UI glitches, missing elements, and unexpected screen modifications are absorbed elegantly by the sequence execution engine without terminating the core process loops.
- **Safe Demonstration Mode**: Built-in `dry_run` configuration safely mimics full pipeline behaviors dynamically on your client screens without formally dispatching the interaction onto a live feed.

---

## 🛠 Requirements
### Prerequisites
- **Python 3.10+** (Make sure to tick "Add Python to PATH" during installation)
- **Node.js** (Required for installing Appium via `npm`)
- **Appium Server 2.x** and `uiautomator2` driver
- Android SDK Platform-Tools (Specifically `adb`)

### Quick Setup
1. **Clone & Environment Setup**
   Open PowerShell or Terminal inside the project directory and install the python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Appium & Sub-Drivers Setup**
   Ensure `npm` is configured on your machine, then run:
   ```bash
   npm i --location=global appium
   appium driver install uiautomator2
   ```

---

## 📱 Device Setup

1. **Enable USB Debugging** on the target Android devices: `Settings` > `Developer Options` > Toggle `USB Debugging`. (For emulators, this is usually enabled by default).
2. Connect your device to your PC or boot up your emulators.
3. Validate connection:
   ```bash
   adb devices
   ```
   *You should see a list of attached devices and their `udid`.*

---

## ⚙ Usage Guide

### 1. `config/config.json`
The central configuration hub for the automation loops.
- `"match_filters"`: Configures which matches the bot enters.
  - `"allowed_sports"`: ["Football", "Tennis", "Basketball", "Baseball", "Cricket"].
  - `"exclude_keywords"`: List of strings (e.g., "Amateur", "U19") used to block non-professional matches.
- `"bot"` parameters dictate execution logic:
  - `"auto_match_selection": true` (Enables the bot to automatically find and enter professional matches from the main screen).
  - `"dry_run": true` (Will simulate interactions but explicitly skip pressing the Send button. Perfect for debugging/client demos).

### 2. `accounts/accounts.json`
Define your emulator profiles and sequential proxy rules.
```json
[
  {
    "username": "user1",
    "emulator_udid": "emulator-5554",
    "proxy": "http://192.168.1.100:8080"
  }
]
```
> **Note**: Leave `"proxy": ""` empty if you do not wish to enforce a dynamic proxy route. If using strictly authenticated IP/Host proxies, it is easiest to run them universally via VPN-wrapper apps directly inside your emulator payload rather than configuring them here.

---

## 🚀 How to Run & Demo Instructions

### To execute a live Demonstration:
1. Review `config.json` and ensure `"dry_run": true` is locked in! 
2. Open your terminal window and launch the local Appium server:
   ```bash
   appium
   ```
3. Boot your Emulator / Plug into your Android device. Wait for it to strictly become fully loaded.
4. Manually open the **Sofascore App** and navigate towards a live match screen.
5. In a secondary terminal window, boot up the Python controller:
   ```bash
   python main.py
   ```
6. **Observe the Bot**: Watch the terminal dynamically print diagnostic `[TRACE]` outputs while the emulator begins scrolling randomly, locking focus modules, and structuring an autonomous text message.

---

## 🛡️ Reliability & Performance

This system has been hardened with a **Performance Intelligence Engine** to ensure production-level stability:

- **Parallel DOM Polling**: High-frequency, non-blocking UI resolution engine that finds elements in sub-second timeframes.
- **Adaptive Selectors**: Intelligent fallback mechanism using ID > Accessibility ID > XPath hierarchy.
- **State-Aware Recovery**: Built-in state machine that automatically detects UI anomalies (e.g., closed panels) and self-heals without human intervention.
- **Strict Performance Bounds**: Hard 5.0s global timeout per action to prevent bot "hanging" during autonomous runs.

## 📊 Validation & Auditing

You can run the full performance audit suite using:
```bash
python test_runner.py
```
This will execute a multi-cycle stress test and produce a **Performance Intelligence Report** with metrics on latency, fallback efficiency, and stability scores.

---

## 🩺 Troubleshooting

- **Device Not Detected**: Ensure `adb devices` lists your device. Try restarting ADB with `adb kill-server` and `adb start-server`.
- **Appium Errors**: Ensure the `appium` server is running and accessible on port `4723`.
- **UI Changes**: If Sofascore updates their app, adjust the adaptive selectors in `utils/selectors.py`.