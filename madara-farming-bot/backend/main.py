from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from bot.travian_bot import TravianBot
import asyncio

app = FastAPI()

# CORS erlaubt Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Travian Bot läuft auf Render!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)

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

    bot = TravianBot(
        username=username,
        password=password,
        server_url=server_url,
        proxy={
            "ip": proxy_ip,
            "port": proxy_port,
            "username": proxy_user,
            "password": proxy_pass,
        } if proxy_ip and proxy_port else None
    )

    success = bot.login()
    if not success:
        return JSONResponse(status_code=401, content={"error": "Login failed"})

    farm_lists = bot.get_farm_lists()
    bots[uid] = {"bot": bot, "task": None}

    return {"uid": uid, "farm_lists": farm_lists}

@app.post("/start")
async def start(uid: str = Form(...), interval_min: int = Form(...), interval_max: int = Form(...), randomize: bool = Form(False)):
    if uid not in bots:
        return JSONResponse(status_code=404, content={"error": "Bot not found"})

    bot = bots[uid]["bot"]

    async def farming_loop():
        while True:
            bot.run_farming()
            wait_time = bot.get_next_wait_time(interval_min, interval_max, randomize)
            await asyncio.sleep(wait_time)

    bots[uid]["task"] = asyncio.create_task(farming_loop())
    return {"status": "started"}

@app.post("/stop")
async def stop(uid: str = Form(...)):
    if uid in bots and bots[uid]["task"]:
        bots[uid]["task"].cancel()
        bots[uid]["task"] = None
        return {"status": "stopped"}
    return JSONResponse(status_code=404, content={"error": "Bot not running"})

@app.post("/status")
async def status(uid: str = Form(...)):
    bot_data = bots.get(uid)
    if not bot_data:
        return JSONResponse(status_code=404, content={"error": "No bot with this UID"})
    is_running = bot_data["task"] is not None
    return {"running": is_running}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)

