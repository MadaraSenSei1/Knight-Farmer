
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from uuid import uuid4
import asyncio
import time
from bot.travian_bot import TravianBot

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

active_bots = {}

class ProxyConfig(BaseModel):
    ip: str
    port: str
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str
    server_url: str
    proxy: ProxyConfig | None = None

class BotControlRequest(BaseModel):
    account_id: str
    interval_min: int
    interval_max: int
    random_delay: bool = True

@app.post("/login")
async def login(data: LoginRequest):
    account_id = str(uuid4())
    bot = TravianBot(
        username=data.username,
        password=data.password,
        server_url=data.server_url,
        proxy=data.proxy.dict() if data.proxy else None
    )

    success = await asyncio.to_thread(bot.login)
    if not success:
        return JSONResponse(status_code=401, content={"detail": "Login failed"})

    farm_lists = await asyncio.to_thread(bot.get_farm_lists)
    active_bots[account_id] = {
        "bot": bot,
        "task": None,
        "next_run": None
    }

    return {"account_id": account_id, "farm_lists": farm_lists}

@app.post("/start-bot")
async def start_bot(data: BotControlRequest):
    entry = active_bots.get(data.account_id)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Bot not found"})

    bot = entry["bot"]

    def update_next_run():
        now = int(time.time())
        wait_min = data.interval_min * 60
        wait_max = data.interval_max * 60
        wait_time = (wait_min + (wait_max - wait_min) * bot.random_float())
        if data.random_delay:
            wait_time += bot.random_offset()
        entry["next_run"] = now + int(wait_time)
        return wait_time

    async def bot_loop():
        while True:
            await asyncio.to_thread(bot.send_farms)
            wait_time = update_next_run()
            await asyncio.sleep(wait_time)

    task = asyncio.create_task(bot_loop())
    entry["task"] = task

    return {"status": "Bot started"}

@app.post("/stop-bot")
async def stop_bot(data: BotControlRequest):
    entry = active_bots.get(data.account_id)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Bot not found"})

    task = entry["task"]
    if task:
        task.cancel()
        entry["task"] = None

    return {"status": "Bot stopped"}

@app.get("/bot-status")
async def bot_status(account_id: str = Query(...)):
    entry = active_bots.get(account_id)
    if not entry:
        return {"active": False}
    task = entry.get("task")
    is_active = task is not None and not task.done()
    return {
        "active": is_active,
        "next_raid_timestamp": entry.get("next_run")
    }
