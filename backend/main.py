from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Kabadi Connect API running"}

POOL_THRESHOLD_KG = 50  # minimum weight a recycler wants per pickup

@app.post("/lots/create")
def create_lot(collector_id: int, material_type: str, weight_kg: float, condition: str, db: Session = Depends(get_db)):
    lot = models.Lot(
        collector_id=collector_id,
        material_type=material_type,
        weight_kg=weight_kg,
        condition=condition,
        status="created"
    )

    if weight_kg < POOL_THRESHOLD_KG:
        pool = db.query(models.Pool).filter(
            models.Pool.material_type == material_type,
            models.Pool.status == "open"
        ).first()

        if not pool:
            pool = models.Pool(material_type=material_type, total_weight_kg=0, status="open")
            db.add(pool)
            db.commit()
            db.refresh(pool)

        pool.total_weight_kg += weight_kg
        if pool.total_weight_kg >= POOL_THRESHOLD_KG:
            pool.status = "matched"

        lot.pool_id = pool.id
        db.add(lot)
        db.commit()
        db.refresh(lot)
        db.refresh(pool)

        return {
            "lot_id": lot.id,
            "pooled": True,
            "pool_id": pool.id,
            "pool_total_weight": pool.total_weight_kg,
            "pool_status": pool.status
        }

    db.add(lot)
    db.commit()
    db.refresh(lot)
    return {"lot_id": lot.id, "pooled": False}

@app.post("/users/create")
def create_user(name: str, phone: str, role: str, db: Session = Depends(get_db)):
    user = models.User(name=name, phone=phone, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "name": user.name, "role": user.role}

BASE_RATES = {
    "PCB": 150,
    "copper_cable": 400,
    "aluminium_cable": 250,
    "battery": 80,
    "LCD": 100,
    "CRT": 50,
    "motor": 200,
    "other": 60
}

CONDITION_MULTIPLIER = {
    "good": 1.0,
    "damaged": 0.7,
    "scrap": 0.5
}

@app.get("/price-estimate")
def price_estimate(material_type: str, weight_kg: float, condition: str):
    base_rate = BASE_RATES.get(material_type, BASE_RATES["other"])
    multiplier = CONDITION_MULTIPLIER.get(condition, 1.0)
    price = base_rate * weight_kg * multiplier
    return {
        "material_type": material_type,
        "weight_kg": weight_kg,
        "condition": condition,
        "price_min": round(price * 0.9, 2),
        "price_max": round(price * 1.1, 2)
    }

@app.post("/recyclers/create")
def create_recycler(name: str, phone: str, accepted_materials: str, db: Session = Depends(get_db)):
    recycler = models.User(
        name=name,
        phone=phone,
        role="recycler",
        accepted_materials=accepted_materials,
        verified=True
    )
    db.add(recycler)
    db.commit()
    db.refresh(recycler)
    return {
        "recycler_id": recycler.id,
        "name": recycler.name,
        "accepted_materials": recycler.accepted_materials
    }

@app.get("/recyclers/match")
def match_recyclers(material_type: str, db: Session = Depends(get_db)):
    recyclers = db.query(models.User).filter(
        models.User.role == "recycler",
        models.User.accepted_materials.contains(material_type)
    ).all()
    return [
        {"recycler_id": r.id, "name": r.name, "accepted_materials": r.accepted_materials}
        for r in recyclers
    ]

import qrcode
import hashlib
import json
import io
import base64

@app.post("/lots/{lot_id}/handover")
def handover_lot(lot_id: int, recycler_id: int, final_price: float, db: Session = Depends(get_db)):
    lot = db.query(models.Lot).filter(models.Lot.id == lot_id).first()
    if not lot:
        return {"error": "Lot not found"}

    lot.status = "handed_over"
    lot.recycler_id = recycler_id
    lot.price_min = final_price
    lot.price_max = final_price

    payload = {
        "lot_id": lot.id,
        "material": lot.material_type,
        "weight_kg": lot.weight_kg,
        "collector_id": lot.collector_id,
        "recycler_id": recycler_id,
        "final_price": final_price
    }

    payload_str = json.dumps(payload, sort_keys=True)
    tamper_hash = hashlib.sha256(payload_str.encode()).hexdigest()

    qr = qrcode.make(payload_str)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    db.commit()
    db.refresh(lot)

    return {
        "lot_id": lot.id,
        "status": lot.status,
        "payload": payload,
        "tamper_hash": tamper_hash,
        "qr_code_base64": qr_base64
    }
