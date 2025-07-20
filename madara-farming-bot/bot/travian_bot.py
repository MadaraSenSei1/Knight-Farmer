
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

class TravianBot:
    def __init__(self, username, password, server_url, proxy=None):
        self.username = username
        self.password = password
        self.server_url = server_url
        self.proxy = proxy
        self.driver = None

    def _get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        if self.proxy:
            proxy_url = f"{self.proxy['ip']}:{self.proxy['port']}"
            chrome_options.add_argument(f"--proxy-server=http://{proxy_url}")
            # Hinweis: Authentifizierte Proxies erfordern ggf. Erweiterungen
        return webdriver.Chrome(options=chrome_options)

    def login(self):
        try:
            self.driver = self._get_driver()
            self.driver.get(self.server_url)
            time.sleep(2)
            self.driver.find_element(By.NAME, "name").send_keys(self.username)
            self.driver.find_element(By.NAME, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(4)
            return "dorf" in self.driver.current_url
        except Exception as e:
            print("Login error:", e)
            return False

    def get_farm_lists(self):
        try:
            self.driver.get(f"{self.server_url}/build.php?tt=99")
            time.sleep(3)
            elements = self.driver.find_elements(By.CLASS_NAME, "listEntry")
            lists = []
            for el in elements:
                name = el.find_element(By.CLASS_NAME, "listName").text.strip()
                lists.append(name)
            return lists
        except Exception as e:
            print("Farm list error:", e)
            return []

    def send_farms(self):
        try:
            self.driver.get(f"{self.server_url}/build.php?tt=99")
            time.sleep(3)
            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox' and contains(@name, 'list')]")
            for cb in checkboxes:
                if not cb.is_selected():
                    cb.click()
            submit = self.driver.find_element(By.XPATH, "//button[contains(@class,'startRaid')]")
            submit.click()
            print("✅ Raids gestartet")
            time.sleep(2)
        except Exception as e:
            print("Farm sending error:", e)

    def random_float(self):
        return random.uniform(0.0, 1.0)

    def random_offset(self):
        return random.randint(-30, 30)
