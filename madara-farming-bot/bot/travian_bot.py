from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
import time

sessions = {}

def create_bot(uid, username, password, server_url, proxy=None):
    options = webdriver.ChromeOptions()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(server_url)
    
    # Beispielhafte Login-Prozedur
    driver.find_element(By.NAME, "name").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "s1").click()
    time.sleep(3)
    
    # Dummy Farm-Listen-Extraktion
    farm_lists = ["Farm 1", "Farm 2", "Farm 3"]
    sessions[uid] = {"driver": driver, "thread": None}
    return farm_lists

def start_bot(uid, min_interval, max_interval, random_offset):
    def loop():
        while True:
            print(f"[{uid}] Sending raid...")
            time.sleep(min_interval * 60)
    t = threading.Thread(target=loop)
    sessions[uid]["thread"] = t
    t.start()

def stop_bot(uid):
    if sessions[uid]["thread"]:
        # In Realität sauberer beenden!
        print(f"[{uid}] Stopping bot...")
