from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from bot.travian_bot import create_bot, start_bot_loop, stop_bot_loop, is_bot_running

app = FastAPI()

# Bot Status
active_bots = {}
paid_users = set()

# Status Check
@app.get("/status")
async def status():
    return {"message": "Travian Bot Backend läuft"}

# LOGIN
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

        print(f"[LOGIN] UID={uid}, SERVER={server_url}, PROXY={proxy}")
        farm_lists = create_bot(uid, username, password, server_url, proxy)
        active_bots[uid] = {"status": "initialized"}

        return {
            "status": "success",
            "uid": uid,
            "farm_lists": farm_lists
        }
    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# START BOT
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
        print(f"[START BOT] UID={uid}, Intervall: {min_interval}-{max_interval}, Random Offset: {random_offset}")
        start_bot_loop(uid, min_interval, max_interval, random_offset)
        active_bots[uid]["status"] = "running"
        return {"status": "Bot gestartet"}
    except Exception as e:
        print("START ERROR:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# STOP BOT
@app.post("/stop")
async def stop(uid: str = Form(...)):
    try:
        print(f"[STOP BOT] UID={uid}")
        stop_bot_loop(uid)
        active_bots[uid]["status"] = "stopped"
        return {"status": "Bot gestoppt"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# BOT STATUS
@app.get("/status/{uid}")
async def get_bot_status(uid: str):
    try:
        status = is_bot_running(uid)
        return {"uid": uid, "running": status}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# STATIC FILES & INDEX HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
