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

@app.get("/dashboard/collector/{collector_id}")
def collector_dashboard(collector_id: int, db: Session = Depends(get_db)):
    lots = db.query(models.Lot).filter(models.Lot.collector_id == collector_id).all()
    total_earnings = sum(l.price_max or 0 for l in lots if l.status == "handed_over")
    return {
        "collector_id": collector_id,
        "total_lots": len(lots),
        "total_earnings": total_earnings,
        "lots": [
            {
                "lot_id": l.id,
                "material_type": l.material_type,
                "weight_kg": l.weight_kg,
                "status": l.status,
                "price": l.price_max
            } for l in lots
        ]
    }

@app.get("/dashboard/recycler/{recycler_id}")
def recycler_dashboard(recycler_id: int, db: Session = Depends(get_db)):
    lots = db.query(models.Lot).filter(models.Lot.recycler_id == recycler_id).all()
    return {
        "recycler_id": recycler_id,
        "total_lots_received": len(lots),
        "lots": [
            {
                "lot_id": l.id,
                "material_type": l.material_type,
                "weight_kg": l.weight_kg,
                "status": l.status,
                "collector_id": l.collector_id
            } for l in lots
        ]
    }

@app.get("/dashboard/admin")
def admin_dashboard(db: Session = Depends(get_db)):
    total_collectors = db.query(models.User).filter(models.User.role == "collector").count()
    total_recyclers = db.query(models.User).filter(models.User.role == "recycler").count()
    total_lots = db.query(models.Lot).count()
    total_weight = sum(l.weight_kg or 0 for l in db.query(models.Lot).all())
    handed_over = db.query(models.Lot).filter(models.Lot.status == "handed_over").count()
    active_pools = db.query(models.Pool).filter(models.Pool.status == "open").count()

    return {
        "total_collectors": total_collectors,
        "total_recyclers": total_recyclers,
        "total_lots": total_lots,
        "total_weight_collected_kg": total_weight,
        "lots_handed_over": handed_over,
        "active_open_pools": active_pools
    }

@app.get("/lots/{lot_id}/fraud-check")
def fraud_check(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(models.Lot).filter(models.Lot.id == lot_id).first()
    if not lot:
        return {"error": "Lot not found"}

    flags = []

    avg_weight = db.query(models.Lot).filter(models.Lot.material_type == lot.material_type).all()
    if avg_weight:
        weights = [l.weight_kg for l in avg_weight if l.weight_kg]
        if weights:
            average = sum(weights) / len(weights)
            if lot.weight_kg > average * 3:
                flags.append("Unusually high weight compared to average for this material")

    base_rate = BASE_RATES.get(lot.material_type, BASE_RATES["other"])
    expected_price = base_rate * lot.weight_kg
    if lot.price_max and (lot.price_max < expected_price * 0.5 or lot.price_max > expected_price * 1.8):
        flags.append("Final price significantly differs from expected fair price range")

    duplicates = db.query(models.Lot).filter(
        models.Lot.collector_id == lot.collector_id,
        models.Lot.material_type == lot.material_type,
        models.Lot.weight_kg == lot.weight_kg,
        models.Lot.id != lot.id
    ).count()
    if duplicates > 0:
        flags.append("Possible duplicate lot detected (same collector, material, and weight)")

    status = "flagged_for_review" if flags else "clean"

    return {
        "lot_id": lot.id,
        "status": status,
        "flags": flags
    }
