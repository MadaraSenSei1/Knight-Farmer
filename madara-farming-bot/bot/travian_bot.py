import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

bots = {}  # uid: TravianBot

class TravianBot:
    def __init__(self, username, password, server_url, proxy=None):
        self.username = username
        self.password = password
        self.server_url = server_url
        self.proxy = proxy
        self.driver = None
        self.running = False
        self.thread = None
        self.min_interval = 60
        self.max_interval = 120
        self.random_offset = True

    def start_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if self.proxy:
            chrome_options.add_argument(f'--proxy-server=http://{self.proxy}')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def login(self):
        self.start_driver()
        self.driver.get(self.server_url)

        time.sleep(3)
        self.driver.find_element(By.NAME, "name").send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password + Keys.RETURN)

        time.sleep(5)
        if "dorf1" not in self.driver.current_url:
            raise Exception("Login fehlgeschlagen")

    def get_farm_lists(self):
        self.driver.get(f"{self.server_url}/build.php?tt=99&id=39")
        time.sleep(2)
        farm_list_elements = self.driver.find_elements(By.CSS_SELECTOR, ".listTitleText")
        return [el.text for el in farm_list_elements]

    def send_farms(self):
        self.driver.get(f"{self.server_url}/build.php?tt=99&id=39")
        time.sleep(2)
        buttons = self.driver.find_elements(By.CSS_SELECTOR, ".startButton")
        for btn in buttons:
            try:
                btn.click()
                time.sleep(1)
            except:
                continue

    def farm_loop(self):
        while self.running:
            try:
                self.send_farms()
                base = random.randint(self.min_interval, self.max_interval)
                offset = random.randint(0, 30) if self.random_offset else 0
                time.sleep(base + offset)
            except Exception as e:
                print("Fehler im Farming-Loop:", e)
                self.running = False
                break

    def start_bot(self, min_interval, max_interval, random_offset=True):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.random_offset = random_offset
        self.running = True
        self.thread = threading.Thread(target=self.farm_loop)
        self.thread.start()

    def stop_bot(self):
        self.running = False
        if self.driver:
            self.driver.quit()

def create_bot(uid, username, password, server_url, proxy=None):
    bot = TravianBot(username, password, server_url, proxy)
    bot.login()
    bots[uid] = bot
    return bot.get_farm_lists()

def start_bot(uid, min_interval, max_interval, random_offset=True):
    if uid in bots:
        bots[uid].start_bot(min_interval, max_interval, random_offset)

def stop_bot(uid):
    if uid in bots:
        bots[uid].stop_bot()
