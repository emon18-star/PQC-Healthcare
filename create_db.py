from app.database.database import Base, engine

# Import all models here
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.audit_log import AuditLog
from app.models.access_request import AccessRequest

def create_database():
    print("Creating database...")
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")


if __name__ == "__main__":
    create_database()