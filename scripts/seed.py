import sys, random, os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal, engine, Base
from app.models import Zone, Scooter, ScooterStatus

zonas = [
    {"nombre": "Centro", "codigo_postal": "28001", "limite_velocidad": 30},
    {"nombre": "Universidad", "codigo_postal": "28002", "limite_velocidad": 20},
    {"nombre": "Parque", "codigo_postal": "28003", "limite_velocidad": 15},
]

scooters = [
    {"numero_serie": "SF-1000", "modelo": "X-Classic"},
    {"numero_serie": "SF-1001", "modelo": "X-Pro"},
    {"numero_serie": "SF-1002", "modelo": "Eco"},
    {"numero_serie": "SF-1003", "modelo": "EcoPlus"},
    {"numero_serie": "SF-1004", "modelo": "Speedster"},
]

def seed(create_tables=False):
    db = SessionLocal()
    try:
        if create_tables:
            print("Creando tablas...")
            Base.metadata.create_all(bind=engine)
        creadas = []
        for zona_d in zonas:
            existe = db.query(Zone).filter(Zone.nombre == zona_d["nombre"]).first()
            if existe:
                print(f"Zona ya existe: {existe.nombre} (id={existe.id})")
                creadas.append(existe)
                continue
            z = Zone(**zona_d)
            db.add(z); db.commit(); db.refresh(z)
            creadas.append(z)
            print(f"Zona creada: {z.nombre} (id={z.id})")
        scooters_creados = []
        for i, s_d in enumerate(scooters):
            existe_s = db.query(Scooter).filter(Scooter.numero_serie == s_d["numero_serie"]).first()
            if existe_s:
                print(f"Scooter ya existe: {existe_s.numero_serie} (id={existe_s.id})")
                scooters_creados.append(existe_s)
                continue
            z_asignada = creadas[i % len(creadas)]
            bateria = random.randint(5,100)
            if bateria <= 0:
                estado = ScooterStatus.sin_bateria
            elif bateria < 15:
                estado = ScooterStatus.mantenimiento
            else:
                estado = random.choice([ScooterStatus.disponible, ScooterStatus.en_uso])
            puntuacion = round(random.uniform(3.0,5.0),2) if random.random() > 0.3 else None
            nuevo = Scooter(numero_serie=s_d["numero_serie"], modelo=s_d["modelo"], bateria=bateria, estado=estado, zona_id=z_asignada.id, puntuacion_usuario=puntuacion)
            db.add(nuevo); db.commit(); db.refresh(nuevo)
            scooters_creados.append(nuevo)
            print(f"Scooter creado: {nuevo.numero_serie} (id={nuevo.id}) en zona {z_asignada.nombre}")
        print(f"\nPoblación completada: Zonas {len(creadas)} - Scooters {len(scooters_creados)}")
    except SQLAlchemyError as e:
        db.rollback(); print("Error durante la población:", e); sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    flag = "--create-tables" in sys.argv
    seed(create_tables=flag)
    print("Hecho.")
