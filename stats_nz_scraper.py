import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver(download_dir):
    options = Options()
    options.add_argument("--headless=new")  # Headless mode for GitHub runner
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def main():
    download_dir = os.getenv("DOWNLOAD_DIR", os.path.join(os.getcwd(), "downloads"))
    os.makedirs(download_dir, exist_ok=True)

    print(f"Download directory: {download_dir}")

    driver = setup_driver(download_dir)
    wait = WebDriverWait(driver, 20)

    try:
        print("Opening website...")
        driver.get("https://infoshare.stats.govt.nz/")
        time.sleep(5)

        print("Navigating through menus...")
        driver.find_element(By.LINK_TEXT, "Browse").click()
        time.sleep(3)
        driver.find_element(By.LINK_TEXT, "Imports and exports").click()
        time.sleep(3)
        driver.find_element(By.LINK_TEXT, "Imports - Summary Data - IMP").click()
        time.sleep(5)
        driver.find_element(By.LINK_TEXT, "Imports - confidential - values and quantities (Annual-Jun)").click()
        time.sleep(7)

        print("Selecting all variables...")
        select_all_elements = driver.find_elements(By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'select all')]")
        for elem in select_all_elements:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                time.sleep(1)
                elem.click()
                time.sleep(1)
            except Exception as e:
                print(f"Could not click one element: {e}")

        print("Selecting CSV format...")
        dropdown = driver.find_element(By.NAME, "ctl00$MainContent$dlOutputOptions")
        select = Select(dropdown)
        for opt in select.options:
            if "csv" in opt.text.lower():
                select.select_by_visible_text(opt.text)
                print(f"Selected format: {opt.text}")
                break

        print("Finding Go button...")
        go_button = driver.find_element(By.XPATH, "//input[contains(@value, 'Go')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", go_button)
        go_button.click()
        print("Clicked Go button, waiting for download...")

        for i in range(40):
            time.sleep(1)
            files = os.listdir(download_dir)
            if files:
                print(f"✅ Download completed: {files}")
                break
            if i % 5 == 0:
                print(f"Waiting... {i}s")
        else:
            print("❌ No download detected")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
