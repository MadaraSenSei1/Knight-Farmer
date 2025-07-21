from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uuid import uuid4

from bot.travian_bot import create_bot, start_bot, stop_bot, get_next_raid_timestamp, travian_login

app = FastAPI()
active_bots = {}

# Static HTML/JS/CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS (lokale Tests & Deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Homepage
@app.get("/")
def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Login + Farmlisten
@app.post("/login", response_class=JSONResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    server_url: str = Form(...),
    proxy_ip: str = Form(""),
    proxy_port: str = Form(""),
    proxy_user: str = Form(""),
    proxy_pass: str = Form(""),
):
    try:
        uid = await travian_login(username, password, server_url, proxy_ip, proxy_port, proxy_user, proxy_pass)
        farm_lists = create_bot(uid, username, password, server_url, proxy_ip, proxy_port, proxy_user, proxy_pass)
        active_bots[uid] = {"status": "initialized", "farm_lists": farm_lists}
        return {"status": "success", "uid": uid, "farm_lists": farm_lists}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# Start Bot
@app.post("/start")
async def start(
    uid: str = Form(...),
    min_interval: int = Form(...),
    max_interval: int = Form(...),
    random_offset: bool = Form(True),
):
    try:
        start_bot(uid, min_interval, max_interval, random_offset)
        active_bots[uid]["status"] = "running"
        return {"status": "started"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# Stop Bot
@app.post("/stop")
async def stop(uid: str = Form(...)):
    try:
        stop_bot(uid)
        active_bots[uid]["status"] = "stopped"
        return {"status": "stopped"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# Bot Status + nächster Raid-Zeitpunkt
@app.get("/status")
async def status(uid: str):
    try:
        if uid in active_bots:
            next_raid = get_next_raid_timestamp(uid)
            return {"status": active_bots[uid]["status"], "next_raid": next_raid}
        return JSONResponse(status_code=404, content={"error": "UID not found"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
