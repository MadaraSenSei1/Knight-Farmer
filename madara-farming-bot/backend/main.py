from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from bot.travian_bot import create_bot, stop_bot
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

active_bots = {}
paid_users = set()

@app.get("/status")
async def status():
    return {"message": "Travian Bot Backend läuft"}

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
            if proxy_user:
                proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
            else:
                proxy = f"http://{proxy_ip}:{proxy_port}"

        farm_lists = create_bot(uid, username, password, server_url, proxy)
        active_bots[uid] = {"status": "initialized"}
        return {
            "status": "success",
            "uid": uid,
            "farm_lists": farm_lists
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/start")
async def start(
    uid: str = Form(...),
    min_interval: int = Form(...),
    max_interval: int = Form(...),
    random_offset: bool = Form(False)
):
    if uid not in paid_users:
        return JSONResponse(status_code=403, content={"error": "Bezahlung erforderlich."})

    try:
        username = active_bots[uid].get("username")
        password = active_bots[uid].get("password")
        server_url = active_bots[uid].get("server_url")
        proxy = active_bots[uid].get("proxy")

        create_bot(uid, username, password, server_url, proxy,
                   min_interval, max_interval, random_offset)
        active_bots[uid]["status"] = "running"
        return {"status": "bot started"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/stop")
async def stop(uid: str = Form(...)):
    stop_bot(uid)
    active_bots[uid]["status"] = "stopped"
    return {"status": "bot stopped"}

@app.post("/payment/confirm")
async def confirm_payment(uid: str = Form(...)):
    paid_users.add(uid)
    return {"status": "confirmed", "uid": uid}
