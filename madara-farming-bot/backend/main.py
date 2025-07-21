from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import paypalrestsdk
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# PayPal Konfiguration
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AccZS6kT4eWWJklsYhrFFhVPhc5ecbmSZext6BFu0GTtwJETs8kyU6TA_0IUlyazAfHwWvwiaQI2wQto",
    "client_secret": "DEIN_CLIENT_SECRET_HIER"  # ersetze das durch deinen echten geheimen Schlüssel
})


@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.post("/verify-payment")
async def verify_payment(request: Request):
    data = await request.json()
    payment_id = data.get("paymentID")

    payment = paypalrestsdk.Payment.find(payment_id)
    if payment and payment.state == "approved":
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Zahlung fehlgeschlagen.")
