from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
import uvicorn
from bot.travian_bot import (
    travian_login,
    start_bot,
    stop_bot,
    get_next_raid_timestamp,
    bots
)

app = FastAPI()

# CORS aktivieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    server_url: str = Form(...),
    proxy_ip: str = Form(None),
    proxy_port: str = Form(None),
    proxy_user: str = Form(None),
    proxy_pass: str = Form(None)
):
    try:
        uid = travian_login(username, password, server_url, proxy_ip, proxy_port, proxy_user, proxy_pass)
        return {
            "success": True,
            "uid": uid,
            "farm_lists": bots[uid]["farm_lists"]
        }
    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=422)


@app.post("/start_bot")
async def start(uid: str = Form(...), min_int: int = Form(...), max_int: int = Form(...), random_offset: bool = Form(...)):
    try:
        start_bot(uid, min_int, max_int, random_offset)
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.post("/stop_bot")
async def stop(uid: str = Form(...)):
    try:
        stop_bot(uid)
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.get("/next_raid")
async def get_raid(uid: str):
    return {"timestamp": get_next_raid_timestamp(uid)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
