import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ---------------------------------------------------------
# 1. DATABASE CONFIGURATION (MySQL Connection)
# ---------------------------------------------------------
# बदल करा: 'root:your_password@localhost:3306/smarthospital'
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://root:root@localhost:3306/smarthospital"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# 2. SQLALCHEMY MODELS (Database Tables)
# ---------------------------------------------------------
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=True)
    password = Column(String(255))
    role = Column(String(50))
    phone = Column(String(20), unique=True, index=True)
    email = Column(String(100), nullable=True)

class DepartmentModel(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(255), nullable=True)

class DoctorModel(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    department = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    qualification = Column(String(100), nullable=True)
    experience = Column(String(50), nullable=True)

class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)
    patient_name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    phone = Column(String(20))
    email = Column(String(100), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patientId = Column(String(50))
    doctorId = Column(String(50))
    departmentId = Column(String(50))
    appointmentDate = Column(String(50))
    appointmentTime = Column(String(50))
    status = Column(String(50), default="Pending")

class QueueTokenModel(Base):
    __tablename__ = "queue_tokens"

    tokenId = Column(Integer, primary_key=True, index=True)
    appointmentId = Column(String(50), nullable=True)
    patientId = Column(String(50))
    tokenNumber = Column(Integer)
    patientName = Column(String(100))
    department = Column(String(100))
    doctorName = Column(String(100))
    status = Column(String(50), default="Waiting")

# ---------------------------------------------------------
# 3. PYDANTIC SCHEMAS (Data Validation Models)
# ---------------------------------------------------------
class LoginRequest(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    password: str

class LoginResponse(BaseModel):
    status: str
    message: str
    user_id: str
    role: str

# Users Schemas
class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    phone: str
    email: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

# Doctor Schemas
class DoctorCreate(BaseModel):
    name: str
    department: str
    phone: Optional[str] = None
    email: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[str] = None

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[str] = None

# Patient Schemas
class PatientCreate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    patient_name: str
    age: int
    gender: str
    phone: str
    email: Optional[str] = None
    department_id: Optional[int] = None
    doctor_id: Optional[int] = None

class PatientUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    patient_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

# Appointment Schemas
class AppointmentCreate(BaseModel):
    patientId: str
    doctorId: str
    departmentId: str
    appointmentDate: str
    appointmentTime: str
    status: Optional[str] = "Pending"

class AppointmentUpdate(BaseModel):
    appointmentDate: Optional[str] = None
    appointmentTime: Optional[str] = None
    status: Optional[str] = None

# Queue Token Schemas
class QueueTokenCreate(BaseModel):
    appointmentId: Optional[str] = None
    patientId: str
    tokenNumber: int
    patientName: str
    department: str
    doctorName: str
    status: Optional[str] = "Waiting"

class QueueTokenUpdate(BaseModel):
    status: Optional[str] = None
    tokenNumber: Optional[int] = None

# ---------------------------------------------------------
# 4. FASTAPI APP INITIALIZATION
# ---------------------------------------------------------
app = FastAPI(title="Smart Hospital Complete Python CRUD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto Create MySQL Tables
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# 5. CRUD ENDPOINTS
# ---------------------------------------------------------

# --- LOGIN ---
@app.post("/login", response_model=LoginResponse, tags=["Auth"])
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = None
    if login_req.phone:
        user = db.query(UserModel).filter(UserModel.phone == login_req.phone).first()
    elif login_req.username:
        user = db.query(UserModel).filter(UserModel.username == login_req.username).first()

    if not user or user.password != login_req.password:
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    return LoginResponse(
        status="success",
        message="Login successful",
        user_id=str(user.id),
        role=user.role
    )

# --- USERS CRUD ---
@app.post("/users", tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"status": "success", "user": db_user}

@app.get("/users", tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()

@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", tags=["Users"])
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return {"status": "success", "message": "User updated", "user": db_user}

@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"status": "success", "message": f"User ID {user_id} deleted"}

# --- DOCTORS CRUD ---
@app.post("/doctors", tags=["Doctors"])
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = DoctorModel(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return {"status": "success", "doctor": db_doctor}

@app.get("/doctors", tags=["Doctors"])
def get_doctors(db: Session = Depends(get_db)):
    return db.query(DoctorModel).all()

@app.get("/doctors/{doctor_id}", tags=["Doctors"])
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.put("/doctors/{doctor_id}", tags=["Doctors"])
def update_doctor(doctor_id: int, doc_update: DoctorUpdate, db: Session = Depends(get_db)):
    db_doctor = db.query(DoctorModel).filter(DoctorModel.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    for key, value in doc_update.dict(exclude_unset=True).items():
        setattr(db_doctor, key, value)

    db.commit()
    db.refresh(db_doctor)
    return {"status": "success", "message": "Doctor updated", "doctor": db_doctor}

@app.delete("/doctors/{doctor_id}", tags=["Doctors"])
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = db.query(DoctorModel).filter(DoctorModel.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(db_doctor)
    db.commit()
    return {"status": "success", "message": f"Doctor ID {doctor_id} deleted"}

# --- PATIENTS CRUD ---
@app.post("/patients", tags=["Patients"])
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = PatientModel(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return {"status": "success", "patient": db_patient}

@app.get("/patients", tags=["Patients"])
def get_patients(db: Session = Depends(get_db)):
    return db.query(PatientModel).all()

@app.get("/patients/{patient_id}", tags=["Patients"])
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/patients/{patient_id}", tags=["Patients"])
def update_patient(patient_id: int, pat_update: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    for key, value in pat_update.dict(exclude_unset=True).items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)
    return {"status": "success", "message": "Patient updated", "patient": db_patient}

@app.delete("/patients/{patient_id}", tags=["Patients"])
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(db_patient)
    db.commit()
    return {"status": "success", "message": f"Patient ID {patient_id} deleted"}

# --- APPOINTMENTS CRUD ---
@app.post("/appointments", tags=["Appointments"])
def create_appointment(app_data: AppointmentCreate, db: Session = Depends(get_db)):
    db_app = AppointmentModel(**app_data.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return {"status": "success", "appointment": db_app}

@app.get("/appointments", tags=["Appointments"])
def get_appointments(db: Session = Depends(get_db)):
    return db.query(AppointmentModel).all()

@app.get("/appointments/{appointment_id}", tags=["Appointments"])
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    app_item = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not app_item:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return app_item

@app.put("/appointments/{appointment_id}", tags=["Appointments"])
def update_appointment(appointment_id: int, app_update: AppointmentUpdate, db: Session = Depends(get_db)):
    db_app = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    for key, value in app_update.dict(exclude_unset=True).items():
        setattr(db_app, key, value)

    db.commit()
    db.refresh(db_app)
    return {"status": "success", "message": "Appointment updated", "appointment": db_app}

@app.delete("/appointments/{appointment_id}", tags=["Appointments"])
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_app = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(db_app)
    db.commit()
    return {"status": "success", "message": f"Appointment ID {appointment_id} deleted"}

# --- QUEUE TOKENS CRUD ---
@app.post("/queue-tokens", tags=["Queue Tokens"])
def create_queue_token(token: QueueTokenCreate, db: Session = Depends(get_db)):
    db_token = QueueTokenModel(**token.dict())
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return {"status": "success", "token": db_token}

@app.get("/queue-tokens", tags=["Queue Tokens"])
def get_queue_tokens(db: Session = Depends(get_db)):
    return db.query(QueueTokenModel).all()

@app.get("/queue-tokens/{token_id}", tags=["Queue Tokens"])
def get_queue_token(token_id: int, db: Session = Depends(get_db)):
    token = db.query(QueueTokenModel).filter(QueueTokenModel.tokenId == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token

@app.put("/queue-tokens/{token_id}", tags=["Queue Tokens"])
def update_queue_token(token_id: int, token_update: QueueTokenUpdate, db: Session = Depends(get_db)):
    db_token = db.query(QueueTokenModel).filter(QueueTokenModel.tokenId == token_id).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    for key, value in token_update.dict(exclude_unset=True).items():
        setattr(db_token, key, value)

    db.commit()
    db.refresh(db_token)
    return {"status": "success", "message": "Queue Token updated", "token": db_token}

@app.delete("/queue-tokens/{token_id}", tags=["Queue Tokens"])
def delete_queue_token(token_id: int, db: Session = Depends(get_db)):
    db_token = db.query(QueueTokenModel).filter(QueueTokenModel.tokenId == token_id).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    db.delete(db_token)
    db.commit()
    return {"status": "success", "message": f"Token ID {token_id} deleted"}

# ---------------------------------------------------------
# 6. SERVER RUN
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("crud_app:app", host="0.0.0.0", port=8000, reload=True)