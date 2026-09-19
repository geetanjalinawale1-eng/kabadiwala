from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Kabadi Connect API running"}
