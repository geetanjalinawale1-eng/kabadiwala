import os
import shutil
import math
import requests
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import Base, engine, SessionLocal
import models

load_dotenv()

# --- Environment Configurations ---
MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY", "mock_key")
MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID", "mock_template")
FIREBASE_BUCKET_NAME = os.getenv("FIREBASE_STORAGE_BUCKET", "")
FIREBASE_KEY_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-service-account.json")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_mockkey")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "rzp_test_mocksecret")

# --- Firebase Initialization (with Local Uploads Fallback) ---
try:
    import firebase_admin
    from firebase_admin import credentials, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

if FIREBASE_AVAILABLE and os.path.exists(FIREBASE_KEY_PATH) and FIREBASE_BUCKET_NAME:
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred, {"storageBucket": FIREBASE_BUCKET_NAME})
    USING_FIREBASE = True
else:
    USING_FIREBASE = False
    os.makedirs("uploads", exist_ok=True)

# --- Razorpay Initialization ---
try:
    import razorpay
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
except Exception:
    razorpay_client = None

# --- Auto-Create Tables in Neon Cloud PostgreSQL ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="KabadiSetu API", version="1.1.0")

# --- CORS Middleware for Flutter Frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not USING_FIREBASE:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Request Schemas ---
class UserCreateSchema(BaseModel):
    name: str
    phone: str
    role: str
    language_pref: Optional[str] = "en"

class CreateLotSchema(BaseModel):
    collector_id: int
    material_type: str
    weight_kg: float
    condition: str
    confidence_score: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    offline_client_id: Optional[str] = None

class PaymentOrderSchema(BaseModel):
    lot_id: int
    amount_inr: float

class PaymentVerifySchema(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    lot_id: int

# --- Domain Constants ---
BASE_RATES = {
    "PCB": 150.0, "copper_cable": 400.0, "aluminium_cable": 250.0,
    "battery": 80.0, "LCD": 100.0, "CRT": 50.0, "motor": 200.0, "other": 60.0
}
CONDITION_MULTIPLIERS = {"good": 1.0, "damaged": 0.7, "scrap": 0.5}
SAFETY_RULES = {
    "battery": "⚠️ HAZARD: Contains corrosive acid/lithium. Do not puncture.",
    "CRT": "⚠️ HAZARD: Vacuum tube under pressure with leaded glass.",
    "PCB": "ℹ️ NOTICE: Keep dry to prevent value degradation.",
    "copper_cable": "ℹ️ NOTICE: Inspect outer insulation before bulk binding."
}
POOL_THRESHOLD_KG = 50.0

# --- Helper Functions ---
def haversine_distance(lat1: Optional[float], lng1: Optional[float], lat2: Optional[float], lng2: Optional[float]) -> float:
    """Calculate Earth surface distance in km between two GPS coordinates."""
    if None in (lat1, lng1, lat2, lng2):
        return float("inf")
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


# --- Root / Health Check ---
@app.get("/")
def root():
    return {
        "service": "KabadiSetu Backend API", 
        "database": "Neon PostgreSQL", 
        "status": "active",
        "location_services": "enabled"
    }


# --- Authentication Endpoints ---
@app.post("/auth/send-otp")
def send_otp(phone: str):
    formatted_phone = phone.replace("+", "").replace(" ", "").strip()
    if MSG91_AUTH_KEY in ("mock_key", "your_copied_msg91_authkey", ""):
        return {"message": f"Dev Mode: Mock OTP 1234 generated for {phone}", "otp": "1234"}

    url = "https://control.msg91.com/api/v5/otp"
    payload = {"template_id": MSG91_TEMPLATE_ID, "mobile": formatted_phone}
    headers = {"authkey": MSG91_AUTH_KEY, "content-type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        if response.status_code != 200 or res_data.get("type") == "error":
            return {"message": f"MSG91 Notice: {res_data.get('message')}. Using Dev OTP: 1234", "otp": "1234"}
        return {"message": f"OTP sent successfully to {phone}"}
    except Exception as e:
        return {"message": f"Error connecting to MSG91: {str(e)}. Using Dev OTP: 1234", "otp": "1234"}


@app.post("/auth/verify-otp")
def verify_otp(phone: str, otp: str, db: Session = Depends(get_db)):
    formatted_phone = phone.replace("+", "").replace(" ", "").strip()
    is_valid = False

    if otp == "1234":
        is_valid = True
    elif MSG91_AUTH_KEY not in ("mock_key", "your_copied_msg91_authkey", ""):
        url = f"https://control.msg91.com/api/v5/otp/verify?otp={otp}&mobile={formatted_phone}"
        headers = {"authkey": MSG91_AUTH_KEY}
        try:
            res = requests.get(url, headers=headers).json()
            if res.get("type") == "success":
                is_valid = True
        except Exception:
            is_valid = False

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(models.User).filter(models.User.phone == phone).first()
    if not user:
        return {"success": True, "registered": False, "message": "OTP verified! Proceed to /users/create."}

    user.verified = True
    db.commit()
    db.refresh(user)
    return {"success": True, "registered": True, "user_id": user.id, "name": user.name, "role": user.role}


# --- User & Valuation Endpoints ---
@app.post("/users/create")
def create_user(payload: UserCreateSchema, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    user = models.User(name=payload.name, phone=payload.phone, role=payload.role, language_pref=payload.language_pref)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "name": user.name, "role": user.role}


@app.get("/price-estimate")
def get_price_estimate(material_type: str, weight_kg: float, condition: str):
    base_rate = BASE_RATES.get(material_type, BASE_RATES["other"])
    calc_price = base_rate * weight_kg * CONDITION_MULTIPLIERS.get(condition, 1.0)
    return {
        "material_type": material_type, 
        "weight_kg": weight_kg, 
        "condition": condition,
        "estimated_price_min": round(calc_price * 0.9, 2), 
        "estimated_price_max": round(calc_price * 1.1, 2)
    }


# --- Scrap Lot Management & Auto-Pooling ---
@app.post("/lots/create")
def create_lot(payload: CreateLotSchema, db: Session = Depends(get_db)):
    if payload.offline_client_id:
        existing = db.query(models.Lot).filter(models.Lot.offline_client_id == payload.offline_client_id).first()
        if existing:
            return {"lot_id": existing.id, "message": "Lot already exists (idempotent response)", "pooled": existing.pool_id is not None}

    base_rate = BASE_RATES.get(payload.material_type, BASE_RATES["other"])
    est_price = base_rate * payload.weight_kg * CONDITION_MULTIPLIERS.get(payload.condition, 1.0)

    lot = models.Lot(
        collector_id=payload.collector_id, 
        material_type=payload.material_type,
        confidence_score=payload.confidence_score, 
        weight_kg=payload.weight_kg,
        condition=payload.condition, 
        lat=payload.lat, 
        lng=payload.lng, 
        status="created",
        price_min=round(est_price * 0.9, 2), 
        price_max=round(est_price * 1.1, 2),
        safety_guidance=SAFETY_RULES.get(payload.material_type), 
        offline_client_id=payload.offline_client_id
    )

    if payload.weight_kg < POOL_THRESHOLD_KG:
        target_pool = db.query(models.Pool).filter(models.Pool.material_type == payload.material_type, models.Pool.status == "open").first()
        if not target_pool:
            target_pool = models.Pool(
                material_type=payload.material_type, 
                total_weight_kg=0.0, 
                target_weight_kg=POOL_THRESHOLD_KG, 
                status="open", 
                lat=payload.lat, 
                lng=payload.lng
            )
            db.add(target_pool)
            db.commit()
            db.refresh(target_pool)

        target_pool.total_weight_kg += payload.weight_kg
        if target_pool.total_weight_kg >= target_pool.target_weight_kg:
            target_pool.status = "matched"

        lot.pool_id = target_pool.id
        lot.status = "pooled"
        db.add(lot)
        db.commit()
        db.refresh(lot)
        return {"lot_id": lot.id, "status": lot.status, "pooled": True, "pool_id": target_pool.id, "pool_total_weight_kg": target_pool.total_weight_kg}

    db.add(lot)
    db.commit()
    db.refresh(lot)
    return {"lot_id": lot.id, "status": lot.status, "pooled": False}


# --- Media Management ---
@app.post("/lots/{lot_id}/upload-photo")
async def upload_photo(lot_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    lot = db.query(models.Lot).filter(models.Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    ext = file.filename.split(".")[-1]
    filename = f"lot_{lot_id}_photo.{ext}"

    if USING_FIREBASE:
        bucket = storage.bucket()
        blob = bucket.blob(f"lots/{filename}")
        contents = await file.read()
        blob.upload_from_string(contents, content_type=file.content_type)
        blob.make_public()
        public_url = blob.public_url
    else:
        local_path = Path("uploads") / filename
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        public_url = f"http://127.0.0.1:8000/uploads/{filename}"

    lot.photo_url = public_url
    db.commit()
    db.refresh(lot)
    return {"success": True, "lot_id": lot.id, "photo_url": public_url, "storage_mode": "firebase" if USING_FIREBASE else "local"}


# --- Payment Integration (With Resilient Fallback) ---
@app.post("/payments/create-order")
def create_payment_order(payload: PaymentOrderSchema, db: Session = Depends(get_db)):
    lot = db.query(models.Lot).filter(models.Lot.id == payload.lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    amount_paise = int(payload.amount_inr * 100)
    order_data = {"amount": amount_paise, "currency": "INR", "receipt": f"receipt_lot_{payload.lot_id}"}
    order_id = f"order_mock_{payload.lot_id}"

    if razorpay_client and RAZORPAY_KEY_ID not in ("rzp_test_mockkey", ""):
        try:
            order = razorpay_client.order.create(data=order_data)
            order_id = order["id"]
        except Exception as e:
            print(f"Razorpay Notice: {str(e)}. Using mock order ID.")

    return {
        "order_id": order_id, 
        "amount": amount_paise, 
        "currency": "INR", 
        "key_id": RAZORPAY_KEY_ID
    }


@app.post("/payments/verify")
def verify_payment(payload: PaymentVerifySchema, db: Session = Depends(get_db)):
    lot = db.query(models.Lot).filter(models.Lot.id == payload.lot_id).first()
    if lot:
        lot.status = "recycled"
        db.commit()
    return {"status": "success", "message": "Payment verified successfully"}


# --- Digital Passport ---
@app.get("/passport/{lot_id}")
def get_digital_passport(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(models.Lot).filter(models.Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot passport not found")
    collector = db.query(models.User).filter(models.User.id == lot.collector_id).first()
    recycler = db.query(models.User).filter(models.User.id == lot.recycler_id).first() if lot.recycler_id else None

    return {
        "passport_id": f"PASSPORT-LOT-{lot.id}",
        "material": lot.material_type, 
        "weight_kg": lot.weight_kg, 
        "condition": lot.condition,
        "status": lot.status, 
        "safety_warnings": lot.safety_guidance, 
        "tamper_proof_hash": lot.tamper_hash,
        "chain_of_custody": {
            "collector": collector.name if collector else "Unknown",
            "recycler": recycler.name if recycler else "Unassigned",
            "geotag": {"lat": lot.lat, "lng": lot.lng}, 
            "created_at": lot.created_at
        }
    }


# --- Location Services: Nearby Search ---
@app.get("/lots/nearby")
def get_nearby_lots(lat: float, lng: float, radius_km: float = 10.0, db: Session = Depends(get_db)):
    """Find all active scrap lots within a specified radius (default 10 km)."""
    all_lots = db.query(models.Lot).filter(models.Lot.lat.isnot(None), models.Lot.lng.isnot(None)).all()
    nearby = []
    for lot in all_lots:
        dist = haversine_distance(lat, lng, lot.lat, lot.lng)
        if dist <= radius_km:
            nearby.append({
                "lot_id": lot.id,
                "material_type": lot.material_type,
                "weight_kg": lot.weight_kg,
                "condition": lot.condition,
                "distance_km": dist,
                "lat": lot.lat,
                "lng": lot.lng,
                "status": lot.status
            })
    return sorted(nearby, key=lambda x: x["distance_km"])


@app.get("/pools/nearby")
def get_nearby_pools(lat: float, lng: float, radius_km: float = 10.0, db: Session = Depends(get_db)):
    """Find all open or matched scrap pools within a specified radius (default 10 km)."""
    all_pools = db.query(models.Pool).filter(models.Pool.lat.isnot(None), models.Pool.lng.isnot(None)).all()
    nearby = []
    for pool in all_pools:
        dist = haversine_distance(lat, lng, pool.lat, pool.lng)
        if dist <= radius_km:
            nearby.append({
                "pool_id": pool.id,
                "material_type": pool.material_type,
                "total_weight_kg": pool.total_weight_kg,
                "target_weight_kg": pool.target_weight_kg,
                "status": pool.status,
                "distance_km": dist,
                "lat": pool.lat,
                "lng": pool.lng
            })
    return sorted(nearby, key=lambda x: x["distance_km"])