from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from bot.travian_bot import create_bot, start_bot, stop_bot
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

active_bots = {}
paid_users = set()

@app.get("/")
async def root():
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

    if proxy_ip and proxy_port:
        proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}" if proxy_user else f"http://{proxy_ip}:{proxy_port}"

    try:
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
        start_bot(uid, min_interval, max_interval, random_offset)
        return {"status": "running"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/stop")
async def stop(uid: str = Form(...)):
    try:
        stop_bot(uid)
        return {"status": "stopped"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/payment_success")
async def payment_success(request: Request):
    data = await request.json()
    uid = data.get("uid")
    if uid:
        paid_users.add(uid)
        return {"message": "Bezahlung akzeptiert"}
    return JSONResponse(status_code=400, content={"error": "UID fehlt"})
