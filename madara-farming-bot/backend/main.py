from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from bot.travian_bot import create_bot, start_bot, stop_bot
import asyncio

app = FastAPI()

# CORS-Konfiguration (für Browserzugriff aus dem Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bot-Speicher
active_bots = {}

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Stelle sicher, dass dein HTML im Ordner /static/index.html liegt
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

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

@app.post("/start")
async def start(uid: str = Form(...), min_interval: int = Form(...), max_interval: int = Form(...), random_offset: bool = Form(True)):
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
        return JSONResponse(status_code=404, content={"error": "UID not found"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# Static HTML-Frontend mounten
app.mount("/", StaticFiles(directory="static", html=True), name="static")

