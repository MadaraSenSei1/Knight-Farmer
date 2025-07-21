import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

bots = {}
next_raid_times = {}

def create_bot(uid, username, password, server_url, proxy=None):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if proxy:
        options.add_argument(f'--proxy-server=http://{proxy}')

    driver = webdriver.Chrome(options=options)
    driver.get(server_url)

    # Travian Login
    driver.find_element(By.NAME, "name").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CLASS_NAME, "login").click()

    time.sleep(5)

    # Suche Farm-Listen
    driver.get(f"{server_url}/build.php?gid=16&tt=99")
    time.sleep(3)

    farm_lists = []
    rows = driver.find_elements(By.CSS_SELECTOR, "div.farmListHeader")
    for row in rows:
        name = row.text.strip()
        list_id = row.find_element(By.XPATH, "..").get_attribute("id").replace("list", "")
        farm_lists.append({"id": list_id, "name": name})

    bots[uid] = {
        "driver": driver,
        "server_url": server_url,
        "farm_lists": farm_lists,
        "running": False,
        "thread": None
    }

    return farm_lists

def send_raids(driver, farm_lists):
    for fl in farm_lists:
        try:
            driver.get(f"{driver.current_url.split('/build')[0]}/build.php?tt=99&id={fl['id']}")
            time.sleep(1)
            btn = driver.find_element(By.NAME, "a")
            btn.click()
        except Exception as e:
            print("Raid error:", e)

def bot_loop(uid, min_int, max_int, random_offset):
    while bots[uid]["running"]:
        interval = random.randint(min_int * 60, max_int * 60)
        if random_offset:
            interval += random.randint(-30, 30)

        next_raid_times[uid] = int(time.time()) + interval

        send_raids(bots[uid]["driver"], bots[uid]["farm_lists"])
        time.sleep(interval)

def start_bot(uid, min_int, max_int, random_offset):
    if uid in bots:
        bots[uid]["running"] = True
        thread = threading.Thread(target=bot_loop, args=(uid, min_int, max_int, random_offset))
        bots[uid]["thread"] = thread
        thread.start()

def stop_bot(uid):
    if uid in bots:
        bots[uid]["running"] = False
        if bots[uid]["thread"]:
            bots[uid]["thread"].join()

def get_next_raid_timestamp(uid):
    return next_raid_times.get(uid)
