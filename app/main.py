from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db

app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Bienvenido a ScooterFlowAPI"}