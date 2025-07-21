import time
import random
import threading
from uuid import uuid4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
__all__ = ["travian_login", "create_bot", "start_bot", "stop_bot", "get_next_raid_timestamp"]

bots = {}
next_raid_times = {}

def travian_login(username, password, server_url, proxy_ip, proxy_port, proxy_user, proxy_pass):
    uid = str(uuid.uuid4())
    proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
    create_bot(uid, username, password, server_url, proxy)
    return uid

def create_bot(uid, username, password, server_url, proxy=None):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    if proxy:
        options.add_argument(f'--proxy-server=http://{proxy}')

    driver = webdriver.Chrome(options=options)
    driver.get(server_url)

    wait = WebDriverWait(driver, 15)

    try:
        # Travian-Login-Felder suchen und ausfüllen
        username_input = wait.until(EC.presence_of_element_located((By.ID, "loginForm_username")))
        password_input = driver.find_element(By.ID, "loginForm_password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()
    except Exception as e:
        print(f"[LOGIN-ERROR] {e}")
        raise Exception("Login-Felder konnten nicht gefunden oder ausgefüllt werden.")

    # Warte auf Redirect nach Login
    time.sleep(5)

    # Farm-Listen laden
    driver.get(f"{server_url}/build.php?id=39&tt=99")
    time.sleep(3)

    farm_lists = []
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "div.farmListHeader")
        for row in rows:
            name = row.text.strip()
            list_id = row.find_element(By.XPATH, "..").get_attribute("id").replace("list", "")
            farm_lists.append({"id": list_id, "name": name})
    except Exception as e:
        print(f"[FARMLIST-ERROR] {e}")

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
            
def travian_login(username, password, server_url, proxy_ip, proxy_port, proxy_user, proxy_pass):
    uid = str(uuid4())
    create_bot(uid, username, password, server_url, {
        "ip": proxy_ip,
        "port": proxy_port,
        "user": proxy_user,
        "pass": proxy_pass,
    })
    return uid

def get_next_raid_timestamp(uid):
    return next_raid_times.get(uid)
