from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import threading
import time

bots = {}
bot_threads = {}


def create_bot(uid, username, password, server_url, proxy=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(server_url)

    try:
        driver.find_element(By.NAME, "name").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "s1").click()
        time.sleep(5)
    except Exception as e:
        driver.quit()
        raise Exception("Login failed")

    farm_lists = [
        {"id": "1", "name": "Main Farm List"},
        {"id": "2", "name": "Secondary Farm List"}
    ]
    bots[uid] = driver
    return farm_lists


def start_bot(uid, min_interval, max_interval, random_offset):
    import random

    def loop():
        while True:
            interval = random.randint(min_interval, max_interval)
            if random_offset:
                interval += random.randint(-30, 30)
            print(f"[Bot {uid}] Sending raid. Next in {interval} seconds.")
            time.sleep(interval)

    thread = threading.Thread(target=loop)
    thread.daemon = True
    thread.start()
    bot_threads[uid] = thread


def stop_bot(uid):
    if uid in bots:
        try:
            bots[uid].quit()
        except:
            pass
        del bots[uid]
    if uid in bot_threads:
        # Real stopping of thread not implemented; placeholder
        del bot_threads[uid]
