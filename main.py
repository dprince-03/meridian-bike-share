from fastapi import FastAPI
from models import create_tables

app = FastAPI(title="Meridian Bike Share API")

create_tables()

@app.get("/")
def root():
    return {"message": "Meridian Bike Share API is running"}