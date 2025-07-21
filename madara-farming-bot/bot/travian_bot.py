import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_bot(uid, username, password, server_url, proxy=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(server_url)

    try:
        driver.find_element(By.NAME, 'name').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.NAME, 's1').click()
        time.sleep(5)
    except Exception as e:
        driver.quit()
        raise Exception("Login failed: " + str(e))

    farm_lists = []
    try:
        driver.get(f"{server_url}/build.php?id=39&tt=99")
        time.sleep(3)
        rows = driver.find_elements(By.CSS_SELECTOR, ".raidList .listEntry")
        for idx, row in enumerate(rows):
            try:
                name = row.find_element(By.CSS_SELECTOR, ".listTitleText").text
                farm_lists.append({"id": idx + 1, "name": name})
            except:
                continue
    except:
        pass

    return farm_lists


def raid_loop(driver, interval_min, interval_max, random_offset):
    while True:
        try:
            driver.get(driver.current_url)
            time.sleep(3)
            buttons = driver.find_elements(By.CSS_SELECTOR, ".startRaid")
            for btn in buttons:
                try:
                    btn.click()
                    time.sleep(1)
                except:
                    continue
        except Exception as e:
            print("Raid loop error:", str(e))

        wait_time = random.randint(interval_min, interval_max)
        if random_offset:
            wait_time += random.randint(0, 30)
        time.sleep(wait_time)


running_threads = {}

def start_bot(uid, min_interval, max_interval, random_offset):
    global running_threads
    if uid not in running_threads:
        raise Exception("Bot not initialized")

    thread = threading.Thread(target=raid_loop, args=(running_threads[uid], min_interval, max_interval, random_offset))
    thread.start()
    running_threads[uid + '_thread'] = thread


def stop_bot(uid):
    global running_threads
    try:
        thread = running_threads.get(uid + '_thread')
        if thread:
            # Selenium does not support clean kill, we rely on browser quitting
            running_threads[uid].quit()
            del running_threads[uid]
            del running_threads[uid + '_thread']
    except Exception as e:
        raise Exception("Error stopping bot: " + str(e))
