from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import threading, time, random

bots = {}

def create_bot(uid, username, password, server_url, proxy=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(options=options)
    driver.get(server_url)

    driver.find_element(By.NAME, "name").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(3)

    farm_lists = ["TestList1", "TestList2"]  # Demo
    bots[uid] = {"driver": driver, "running": False}
    return farm_lists

def raid_loop(uid, min_interval, max_interval, random_offset):
    bot = bots[uid]
    bot["running"] = True

    while bot["running"]:
        print(f"[{uid}] → Sende Raids...")

        interval = random.randint(min_interval, max_interval)
        if random_offset:
            interval += random.randint(0, 30)

        time.sleep(interval)

def start_bot(uid, min_interval, max_interval, random_offset):
    thread = threading.Thread(target=raid_loop, args=(uid, min_interval, max_interval, random_offset))
    thread.start()

def stop_bot(uid):
    bots[uid]["running"] = False
