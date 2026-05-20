from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# ---------- CONFIG ----------
SEARCH_FILE = "C:/Users/Lucio/momproject/US_Overall_Search.txt"

# MEDLINE Advanced Search URL (the one you just sent)
OVID_MEDLINE_URL = "https://resources.library.ubc.ca/139/"

# Search box <textarea id="ovidclassis_focus">
SEARCH_BOX_BY = By.XPATH
SEARCH_BOX_VALUE = "//textarea[contains(@id,'focus') or contains(@id,'search')] | //input[@type='text']"

# Search button <button id="main-search-button-ovidclassic">
SEARCH_BUTTON_BY = By.ID
SEARCH_BUTTON_VALUE = "main-search-button-ovidclassic"

# Your Chrome profile (from chrome://version)
# CHROME_USER_DATA_DIR = r"C:\Users\Lucio\AppData\Local\Google\Chrome\User Data"
# CHROME_PROFILE_DIR = "Default"

# ---------- START CHROME WITH YOUR REAL PROFILE ----------
# options = webdriver.ChromeOptions()
# options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")
# options.add_argument(f"--profile-directory={CHROME_PROFILE_DIR}")
# options.add_argument("--no-first-run")
# options.add_argument("--no-default-browser-check")
# options.add_argument("--disable-session-crashed-bubble")



driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    # options=options,
)
wait = WebDriverWait(driver, 20)

print("✅ Launched Chrome with your real profile (should reuse your Ovid login if cached).")

driver.get("about:blank")
driver.get(OVID_MEDLINE_URL)

# Go straight to MEDLINE Advanced Search
print(f"➡️ Navigating to MEDLINE URL: {OVID_MEDLINE_URL}")
driver.get(OVID_MEDLINE_URL)
print("Current URL: ", driver.current_url)

# If your institution redirects to a login page, log in once in THIS window.
input("🔑 If you see a login page, log in now in the Chrome window, then press ENTER here... ")
print("Waiting for Ovid to finish login redirect...")
time.sleep(5)
  
wait.until(lambda d: "ovid" in d.current_url.lower())
time.sleep(5)

def find_search_box():
    driver.switch_to.default_content()

    selectors = [
        "//textarea[contains(@id,'focus') or contains(@id,'search')]",
        "//input[@type='text']"
    ]

    # 1. try main DOM
    for sel in selectors:
        els = driver.find_elements(By.XPATH, sel)
        if els:
            return els[0]

    # 2. try iframe(s)
    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    for frame in iframes:
        driver.switch_to.default_content()
        driver.switch_to.frame(frame)

        for sel in selectors:
            els = driver.find_elements(By.XPATH, sel)
            if els:
                return els[0]

    driver.switch_to.default_content()
    return None

def find_in_frames(driver):
    driver.switch_to.default_content()

    selectors = [
        "//textarea",
        "//input[@type='text']"
    ]

    def valid(el):
        try:
            return el.is_displayed() and el.is_enabled()
        except:
            return False

    # main DOM
    for sel in selectors:
        els = driver.find_elements(By.XPATH, sel)
        for el in els:
            if valid(el):
                return el

    # iframe search
    frames = driver.find_elements(By.TAG_NAME, "iframe")

    for frame in frames:
        driver.switch_to.default_content()
        driver.switch_to.frame(frame)

        for sel in selectors:
            els = driver.find_elements(By.XPATH, sel)
            for el in els:
                if valid(el):
                    return el

    driver.switch_to.default_content()
    return None

def run_cmd(cmd: str):
    print(f"\nRunning: {cmd}")

    # --- FIND SEARCH BOX ---
    box = None

    for _ in range(30):
        box = find_in_frames(driver)
        if box:
            break
        time.sleep(1)

    if not box:
        driver.save_screenshot("ovid_debug.png")
        raise Exception("Search box not found anywhere (saved screenshot)")

    # --- FORCE REAL USER INTERACTION ---
    driver.switch_to.default_content()

    driver.execute_script("arguments[0].scrollIntoView(true);", box)
    driver.execute_script("arguments[0].focus();", box)

    time.sleep(0.2)

    driver.execute_script("arguments[0].value = '';", box)
    box.send_keys(cmd)

    time.sleep(0.2)

    box.send_keys("\n")

    time.sleep(1)


# ---------- LOAD COMMANDS ----------
with open(SEARCH_FILE, encoding="utf-8") as f:
    commands = [line.strip() for line in f if line.strip()]

print(f"📄 Loaded {len(commands)} lines from {SEARCH_FILE}")

# ---------- RUN THEM ----------
for cmd in commands:
    run_cmd(cmd)

print("\n🎉 All commands processed. Check the Ovid history in the Chrome window.")
input("Press ENTER to close the browser...")
# driver.quit()  # uncomment if you want it to close the window at the end
