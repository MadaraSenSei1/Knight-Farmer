from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from bot.travian_bot import create_bot, start_bot, stop_bot, get_bot_status
import asyncio

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

active_bots = {}
paid_users = set()

@app.get("/")
async def root():
    return HTMLResponse(open("static/index.html").read())

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

@app.post("/pay")
async def pay(uid: str = Form(...)):
    paid_users.add(uid)
    return {"status": "paid"}

@app.get("/bot_status")
async def bot_status(uid: str):
    return get_bot_status(uid)
