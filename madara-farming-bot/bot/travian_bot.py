import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TravianBot:
    def __init__(self, username, password, server_url, proxy=None):
        self.username = username
        self.password = password
        self.server_url = server_url
        self.proxy = proxy
        self.driver = None
        self.next_raid_timestamp = None

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if self.proxy:
            proxy_auth = f"{self.proxy['username']}:{self.proxy['password']}@{self.proxy['ip']}:{self.proxy['port']}"
            chrome_options.add_argument(f'--proxy-server=http://{self.proxy["ip"]}:{self.proxy["port"]}')
            # Hinweis: Für Auth-Proxies ist ein Plugin notwendig (nicht in headless mode direkt nutzbar)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def login(self):
        try:
            self.setup_driver()
            self.driver.get(self.server_url)
            time.sleep(2)

            self.driver.find_element(By.NAME, "name").send_keys(self.username)
            self.driver.find_element(By.NAME, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

            time.sleep(4)
            if "dorf1.php" in self.driver.current_url:
                return True
            return False
        except WebDriverException as e:
            print("Login error:", e)
            return False

    def get_farm_lists(self):
        try:
            self.driver.get(f"{self.server_url}/build.php?tt=99&id=39")
            time.sleep(3)
            lists = self.driver.find_elements(By.CLASS_NAME, "listTitle")
            return [l.text for l in lists]
        except Exception as e:
            print("Fehler beim Farm-Listen-Abruf:", e)
            return []

    def run_farming(self):
        try:
            self.driver.get(f"{self.server_url}/build.php?tt=99&id=39")
            time.sleep(3)
            raid_buttons = self.driver.find_elements(By.CLASS_NAME, "startRaid")
            for btn in raid_buttons:
                try:
                    btn.click()
                    time.sleep(0.5)
                except Exception:
                    continue
        except Exception as e:
            print("Fehler beim Raiden:", e)

    def get_next_wait_time(self, interval_min, interval_max, randomize=False):
        wait = random.randint(interval_min * 60, interval_max * 60)
        if randomize:
            wait += random.randint(-30, 30)
        self.next_raid_timestamp = int(time.time() + wait)
        return wait

    def stop(self):
        if self.driver:
            self.driver.quit()
