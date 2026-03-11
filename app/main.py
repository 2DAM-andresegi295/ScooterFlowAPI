from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from app.models import Scooter, Zone, ScooterStatus
import swagger_ui_bundle

app = FastAPI(docs_url=None)
app.openapi_version = "3.0.3"

SWAGGER_UI_PACKAGE_DIR = Path(swagger_ui_bundle.__file__).resolve().parent
SWAGGER_UI_VENDOR_DIR = SWAGGER_UI_PACKAGE_DIR / "vendor"
SWAGGER_UI_DIST = next(
    (path for path in SWAGGER_UI_VENDOR_DIR.iterdir() if path.is_dir()),
    SWAGGER_UI_PACKAGE_DIR,
) if SWAGGER_UI_VENDOR_DIR.exists() else SWAGGER_UI_PACKAGE_DIR
app.mount("/swagger-static", StaticFiles(directory=str(SWAGGER_UI_DIST)), name="swagger-static")


class ScooterCreate(BaseModel):
    numero_serie: str
    modelo: str
    bateria: int
    estado: ScooterStatus
    zona_id: int
    puntuacion_usuario: Optional[float] = None

    @field_validator('bateria')
    @classmethod
    def bateria_range(cls, v):
        if v < 0 or v > 100:
            raise ValueError('La batería debe estar entre 0 y 100')
        return v


class ZoneCreate(BaseModel):
    nombre: str
    codigo_postal: str
    limite_velocidad: int

@app.get("/")
def read_root():
    return {"message": "Bienvenido a ScooterFlowAPI"}


@app.get("/scooters/")
def list_scooters(db: Session = Depends(get_db)):
    return db.query(Scooter).all()


@app.post("/scooters/", status_code=201,)
def create_scooter(scooter: ScooterCreate, db: Session = Depends(get_db)):
    db_scooter = Scooter(**scooter.model_dump())
    db.add(db_scooter)
    db.commit()
    db.refresh(db_scooter)
    return db_scooter


@app.get("/zonas/")
def list_zones(db: Session = Depends(get_db)):
    return db.query(Zone).all()


@app.post("/zonas/", status_code=201)
def create_zone(zone: ZoneCreate, db: Session = Depends(get_db)):
    db_zone = Zone(**zone.model_dump())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@app.post("/zonas/{zona_id}/mantenimiento")
def mantenimiento_zona(zona_id: int, db: Session = Depends(get_db)):
    scooters = db.query(Scooter).filter(Scooter.zona_id == zona_id, Scooter.bateria < 15).all()
    for scooter in scooters:
        scooter.estado = ScooterStatus.mantenimiento
    db.commit()
    return {"actualizados": len(scooters)}


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/swagger-static/swagger-ui-bundle.js",
        swagger_css_url="/swagger-static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()
