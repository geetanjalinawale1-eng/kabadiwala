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
