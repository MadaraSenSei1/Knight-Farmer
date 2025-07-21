from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import os
from dotenv import load_dotenv
from bot.travian_bot import create_bot, start_bot, stop_bot

load_dotenv()
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Status Check
@app.get("/status")
async def status():
    return {"message": "Travian Bot Backend läuft"}

# Speicher für aktive Bots
active_bots = {}
paid_users = set()

# Login Endpoint
@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    server_url: str = Form(...),
    proxy_ip: str = Form(""),
    proxy_port: str = Form(""),
    proxy_user: str = Form(""),
    proxy_pass: str = Form("")
):
    uid = str(uuid4())
    proxy = None

    try:
        if proxy_ip and proxy_port:
            proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}" if proxy_user else f"http://{proxy_ip}:{proxy_port}"
            print(f"[LOGIN] Mit Proxy: {proxy}")
        else:
            print("[LOGIN] Ohne Proxy")

        # Starte Bot
        farm_lists = create_bot(uid, username, password, server_url, proxy)

        active_bots[uid] = {"status": "initialized"}
        return {
            "status": "success",
            "uid": uid,
            "farm_lists": farm_lists
        }

    except Exception as e:
        print("[LOGIN ERROR]:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# Bot starten
@app.post("/start")
async def start(
    uid: str = Form(...),
    min_interval: int = Form(...),
    max_interval: int = Form(...),
    random_offset: bool = Form(False)
):
    if uid not in active_bots:
        return JSONResponse(status_code=403, content={"error": "Ungültige UID"})

    try:
        start_bot(uid, min_interval, max_interval, random_offset)
        active_bots[uid]["status"] = "running"
        return {"status": "started"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Bot stoppen
@app.post("/stop")
async def stop(uid: str = Form(...)):
    try:
        stop_bot(uid)
        active_bots[uid]["status"] = "stopped"
        return {"status": "stopped"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
