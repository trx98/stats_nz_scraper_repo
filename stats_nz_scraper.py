from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import time, os

def setup_driver(download_dir):
    options = Options()
    options.add_argument("--headless=new")
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

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver


def main():
    download_dir = os.environ.get("DOWNLOAD_DIR", os.path.join(os.getcwd(), "downloads"))
    os.makedirs(download_dir, exist_ok=True)
    driver = setup_driver(download_dir)

    try:
        print("Opening site...")
        driver.get("https://infoshare.stats.govt.nz/")
        time.sleep(5)

        driver.find_element(By.LINK_TEXT, "Browse").click()
        time.sleep(3)
        driver.find_element(By.LINK_TEXT, "Imports and exports").click()
        time.sleep(3)
        driver.find_element(By.LINK_TEXT, "Imports - Summary Data - IMP").click()
        time.sleep(5)
        driver.find_element(By.LINK_TEXT, "Imports - confidential - values and quantities (Annual-Jun)").click()
        time.sleep(7)

        print("Clicking all 'Select all' buttons...")
        buttons = driver.find_elements(By.XPATH, "//span[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'select all')]")
        for b in buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", b)
                time.sleep(1)
                b.click()
                time.sleep(1)
            except Exception as e:
                print("Error clicking button:", e)

        dropdown = driver.find_element(By.NAME, "ctl00$MainContent$dlOutputOptions")
        select = Select(dropdown)
        found = False
        for text in ["Comma delimited (.csv)", "CSV file", ".csv", "csv"]:
            try:
                select.select_by_visible_text(text)
                print("Selected", text)
                found = True
                break
            except:
                continue
        if not found:
            for opt in select.options:
                if "csv" in opt.text.lower():
                    select.select_by_visible_text(opt.text)
                    print("Selected", opt.text)
                    break

        print("Looking for Go button...")
        selectors = [
            "//input[@type='submit' and contains(@value,'Go')]",
            "//input[contains(@value,'Go')]",
            "//button[contains(text(),'Go')]",
            "//*[@id='ctl00_MainContent_btnGo']",
            "//input[@name='ctl00$MainContent$btnGo']"
        ]

        go_button = None
        for s in selectors:
            try:
                go_button = driver.find_element(By.XPATH, s)
                break
            except:
                continue

        if go_button:
            driver.execute_script("arguments[0].scrollIntoView(true);", go_button)
            time.sleep(1)
            go_button.click()
            print("Clicked Go button")
        else:
            print("Go button not found")

        print("Waiting for download...")
        for i in range(60):
            if os.listdir(download_dir):
                print("Download complete:", os.listdir(download_dir))
                break
            time.sleep(1)
        else:
            print("No file downloaded within 60 seconds")

    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()
        print("Done")


if __name__ == "__main__":
    main()
