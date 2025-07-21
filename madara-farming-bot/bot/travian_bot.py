import time
import random
from threading import Thread
from typing import Optional

def create_bot(uid, username, password, server_url, proxy=None):
    # Diese Funktion simuliert das Abrufen von Farm-Listen nach erfolgreichem Login
    print(f"[INFO] Bot erstellt für {username}@{server_url} mit Proxy: {proxy}")
    return ["Farm A", "Farm B", "Farm C"]

def start_bot(uid, min_interval, max_interval, random_offset=False):
    def run():
        print(f"[BOT {uid}] gestartet mit Intervall {min_interval}-{max_interval} Sekunden (Zufall: {random_offset})")
        while True:
            interval = random.randint(min_interval, max_interval)
            if random_offset:
                offset = random.randint(0, 30)
                interval += offset
            print(f"[BOT {uid}] Raid gesendet. Warte {interval} Sekunden...")
            time.sleep(interval)
    
    thread = Thread(target=run, daemon=True)
    thread.start()

def stop_bot(uid):
    print(f"[BOT {uid}] gestoppt. (Hinweis: In dieser einfachen Version läuft der Thread weiter.)")
    # In einem echten Setup wäre hier eine Mechanik zur Beendigung erforderlich
