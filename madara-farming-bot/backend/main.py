from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from bot.travian_bot import create_bot, start_bot, stop_bot, get_next_raid_timestamp

app = FastAPI()

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS für lokale Tests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Speichert aktive Bots
active_bots = {}

@app.get("/")
def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/login")
async def login(data: dict):
    # Hole alle Daten aus dem `data`-Dict
    username = data.get("username")
    password = data.get("password")
    server_url = data.get("server_url")
    proxy_ip = data.get("proxy_ip")
    proxy_port = data.get("proxy_port")
    proxy_user = data.get("proxy_user")
    proxy_pass = data.get("proxy_pass")

    # Logik: Login in Travian durchführen
    try:
        uid = await travian_login(username, password, server_url, proxy_ip, proxy_port, proxy_user, proxy_pass)
        return { "status": "success", "uid": uid }
    except Exception as e:
        return { "status": "error", "error": str(e) }

    try:
        farm_lists = create_bot(uid, username, password, server_url, proxy)
        active_bots[uid] = {"status": "initialized"}
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
            next_raid = get_next_raid_time(uid)
            return {"status": active_bots[uid]["status"], "next_raid": next_raid}
        return JSONResponse(status_code=404, content={"error": "UID not found"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
