from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from bot.travian_bot import create_bot, start_bot, stop_bot

app = FastAPI()

# Statische Dateien (z. B. index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_bots = {}
paid_users = set()

@app.get("/")
def root():
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
        proxy = f"{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}" if proxy_user else f"{proxy_ip}:{proxy_port}"

    try:
        farm_lists = create_bot(uid, username, password, server_url, proxy)
        active_bots[uid] = {
            "status": "initialized",
            "interval_task": None
        }
        return {"status": "success", "uid": uid, "farm_lists": farm_lists}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/pay")
async def confirm_payment(uid: str):
    paid_users.add(uid)
    return {"status": "paid"}

@app.post("/start")
async def start(uid: str = Form(...), min_interval: int = Form(...), max_interval: int = Form(...), random_offset: bool = Form(...)):
    if uid not in paid_users:
        return JSONResponse(status_code=403, content={"error": "Zahlung erforderlich"})

    try:
        start_bot(uid, min_interval, max_interval, random_offset)
        active_bots[uid]["status"] = "running"
        return {"status": "started"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/stop")
async def stop(uid: str = Form(...)):
    try:
        stop_bot(uid)
        active_bots[uid]["status"] = "stopped"
        return {"status": "stopped"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/status")
async def status(uid: str):
    try:
        if uid in active_bots:
            return {"status": active_bots[uid]["status"]}
        return JSONResponse(status_code=404, content={"error": "UID nicht gefunden"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
        app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
