from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from bot.travian_bot import create_bot, start_bot, stop_bot
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

active_bots = {}
paid_users = set()

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
    if proxy_ip and proxy_port:
        proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}" if proxy_user else f"http://{proxy_ip}:{proxy_port}"

    try:
        farm_lists = create_bot(uid, username, password, server_url, proxy)
        active_bots[uid] = {"status": "initialized"}
        return {"status": "success", "uid": uid, "farm_lists": farm_lists}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/pay")
async def pay(uid: str = Form(...)):
    paid_users.add(uid)
    return {"status": "paid"}

@app.post("/start")
async def start(
    uid: str = Form(...),
    min_interval: int = Form(...),
    max_interval: int = Form(...),
    random_offset: bool = Form(False)
):
    if uid not in paid_users:
        return JSONResponse(status_code=403, content={"error": "Payment required"})

    try:
        start_bot(uid, min_interval, max_interval, random_offset)
        active_bots[uid]["status"] = "running"
        return {"status": "started"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/stop")
async def stop(uid: str = Form(...)):
    try:
        stop_bot(uid)
        active_bots[uid]["status"] = "stopped"
        return {"status": "stopped"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def index():
    return FileResponse("static/index.html")
