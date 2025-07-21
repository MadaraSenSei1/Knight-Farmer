import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

bots = {}

# Bot erstellen und Farm-Liste laden
def create_bot(uid, username, password, server_url, proxy=None):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(server_url)
        time.sleep(3)

        # Login-Seite ausfüllen
        driver.find_element(By.NAME, "name").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "s1").click()

        time.sleep(5)

        # Farm-Liste aufrufen
        driver.get(f"{server_url}/build.php?tt=99")
        time.sleep(3)

        farm_list_elements = driver.find_elements(By.CSS_SELECTOR, "#raidList .listTitle")
        farm_lists = [el.text for el in farm_list_elements if el.text.strip() != ""]

        bots[uid] = {
            "driver": driver,
            "running": False,
            "thread": None
        }

        return farm_lists

    except Exception as e:
        driver.quit()
        raise Exception(f"Bot creation failed: {e}")

# Farming-Schleife

def bot_loop(uid, min_interval, max_interval, random_offset):
    import random
    driver = bots[uid]["driver"]
    bots[uid]["running"] = True

    try:
        while bots[uid]["running"]:
            # Farm-Button klicken
            driver.get(driver.current_url)
            time.sleep(3)

            buttons = driver.find_elements(By.CSS_SELECTOR, ".startRaid")
            for btn in buttons:
                try:
                    btn.click()
                    time.sleep(0.5)
                except:
                    continue

            wait = random.randint(min_interval, max_interval)
            if random_offset:
                wait += random.randint(0, 30)

            print(f"[Bot {uid}] Waiting {wait} seconds before next raid")
            time.sleep(wait)

    except Exception as e:
        print(f"[Bot {uid}] ERROR: {e}")
        bots[uid]["running"] = False

# Bot starten
def start_bot(uid, min_interval, max_interval, random_offset):
    if uid in bots and not bots[uid]["running"]:
        t = threading.Thread(target=bot_loop, args=(uid, min_interval, max_interval, random_offset))
        bots[uid]["thread"] = t
        t.start()

# Bot stoppen
def stop_bot(uid):
    if uid in bots:
        bots[uid]["running"] = False
        time.sleep(2)
        bots[uid]["driver"].quit()
        del bots[uid]
