from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import engine, Base, get_db
import models
import schemas

# Automatic MySQL table creation if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Hospital FastAPI Complete CRUD Backend (MySQL)")

@app.get("/")
def get_root():
    return {"message": "Smart Hospital Complete CRUD API with MySQL is Online"}

@app.get("/health")
def check_health():
    return {"status": "OK"}

# =========================================================
# 1. AUTH & LOGIN
# =========================================================
@app.post("/login", response_model=schemas.LoginResponse, tags=["Auth"])
def login(login_req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = None
    if login_req.phone:
        user = db.query(models.UserModel).filter(models.UserModel.phone == login_req.phone).first()
    elif login_req.username:
        user = db.query(models.UserModel).filter(models.UserModel.username == login_req.username).first()

    if not user or user.password != login_req.password:
        raise HTTPException(status_code=400, detail="Invalid Username/Phone or Password")

    return schemas.LoginResponse(
        status="success",
        message="Login successful",
        user_id=str(user.id),
        role=user.role
    )

# =========================================================
# 2. USERS CRUD
# =========================================================
@app.post("/users", response_model=schemas.UserSchema, tags=["Users"])
def create_user(user: schemas.UserSchema, db: Session = Depends(get_db)):
    db_user = models.UserModel(**user.dict(exclude={"id"}))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    user.id = str(db_user.id)
    return user

@app.get("/users", response_model=List[schemas.UserSchema], tags=["Users"])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.UserModel).all()
    res = []
    for u in users:
        u_schema = schemas.UserSchema.from_orm(u)
        u_schema.id = str(u.id)
        res.append(u_schema)
    return res

@app.get("/users/{user_id}", response_model=schemas.UserSchema, tags=["Users"])
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    res = schemas.UserSchema.from_orm(user)
    res.id = str(user.id)
    return res

@app.put("/users/{user_id}", response_model=schemas.UserSchema, tags=["Users"])
def update_user(user_id: int, user_update: schemas.UserUpdateSchema, db: Session = Depends(get_db)):
    db_user = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    res = schemas.UserSchema.from_orm(db_user)
    res.id = str(db_user.id)
    return res

@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"status": "success", "message": f"User ID {user_id} deleted"}

# =========================================================
# 3. DEPARTMENTS CRUD
# =========================================================
@app.post("/departments", response_model=schemas.DepartmentSchema, tags=["Departments"])
def create_department(dept: schemas.DepartmentSchema, db: Session = Depends(get_db)):
    db_dept = models.DepartmentModel(name=dept.name, description=dept.description)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    dept.id = str(db_dept.id)
    return dept

@app.get("/departments", response_model=List[schemas.DepartmentSchema], tags=["Departments"])
def get_all_departments(db: Session = Depends(get_db)):
    depts = db.query(models.DepartmentModel).all()
    res = []
    for d in depts:
        d_schema = schemas.DepartmentSchema.from_orm(d)
        d_schema.id = str(d.id)
        res.append(d_schema)
    return res

@app.get("/departments/{dept_id}", response_model=schemas.DepartmentSchema, tags=["Departments"])
def get_department_by_id(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(models.DepartmentModel).filter(models.DepartmentModel.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    res = schemas.DepartmentSchema.from_orm(dept)
    res.id = str(dept.id)
    return res

@app.put("/departments/{dept_id}", response_model=schemas.DepartmentSchema, tags=["Departments"])
def update_department(dept_id: int, dept_update: schemas.DepartmentUpdateSchema, db: Session = Depends(get_db)):
    db_dept = db.query(models.DepartmentModel).filter(models.DepartmentModel.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")

    update_data = dept_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dept, key, value)

    db.commit()
    db.refresh(db_dept)
    res = schemas.DepartmentSchema.from_orm(db_dept)
    res.id = str(db_dept.id)
    return res

@app.delete("/departments/{dept_id}", tags=["Departments"])
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    db_dept = db.query(models.DepartmentModel).filter(models.DepartmentModel.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(db_dept)
    db.commit()
    return {"status": "success", "message": f"Department ID {dept_id} deleted"}

# =========================================================
# 4. DOCTORS CRUD
# =========================================================
@app.post("/doctors", response_model=schemas.DoctorSchema, tags=["Doctors"])
def create_doctor(doc: schemas.DoctorSchema, db: Session = Depends(get_db)):
    db_doc = models.DoctorModel(**doc.dict(exclude={"id"}))
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    doc.id = str(db_doc.id)
    return doc

@app.get("/doctors", response_model=List[schemas.DoctorSchema], tags=["Doctors"])
def get_all_doctors(db: Session = Depends(get_db)):
    docs = db.query(models.DoctorModel).all()
    res = []
    for d in docs:
        d_schema = schemas.DoctorSchema.from_orm(d)
        d_schema.id = str(d.id)
        res.append(d_schema)
    return res

@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorSchema, tags=["Doctors"])
def get_doctor_by_id(doctor_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.DoctorModel).filter(models.DoctorModel.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    res = schemas.DoctorSchema.from_orm(doc)
    res.id = str(doc.id)
    return res

@app.put("/doctors/{doctor_id}", response_model=schemas.DoctorSchema, tags=["Doctors"])
def update_doctor(doctor_id: int, doc_update: schemas.DoctorUpdateSchema, db: Session = Depends(get_db)):
    db_doc = db.query(models.DoctorModel).filter(models.DoctorModel.id == doctor_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    update_data = doc_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doc, key, value)

    db.commit()
    db.refresh(db_doc)
    res = schemas.DoctorSchema.from_orm(db_doc)
    res.id = str(db_doc.id)
    return res

@app.delete("/doctors/{doctor_id}", tags=["Doctors"])
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doc = db.query(models.DoctorModel).filter(models.DoctorModel.id == doctor_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(db_doc)
    db.commit()
    return {"status": "success", "message": f"Doctor ID {doctor_id} deleted"}

# =========================================================
# 5. PATIENTS CRUD
# =========================================================
@app.post("/patients", response_model=schemas.PatientSchema, tags=["Patients"])
def create_patient(pat: schemas.PatientSchema, db: Session = Depends(get_db)):
    name = pat.patient_name or pat.fullName or "Patient"
    db_pat = models.PatientModel(
        username=pat.username,
        password=pat.password,
        patient_name=name,
        age=pat.age,
        gender=pat.gender,
        phone=pat.phone,
        email=pat.email,
        department_id=pat.department_id,
        doctor_id=pat.doctor_id
    )
    db.add(db_pat)
    db.commit()
    db.refresh(db_pat)
    pat.id = str(db_pat.id)
    pat.patient_name = name
    return pat

@app.get("/patients", response_model=List[schemas.PatientSchema], tags=["Patients"])
def get_all_patients(db: Session = Depends(get_db)):
    pats = db.query(models.PatientModel).all()
    res = []
    for p in pats:
        p_schema = schemas.PatientSchema.from_orm(p)
        p_schema.id = str(p.id)
        res.append(p_schema)
    return res

@app.get("/patients/{patient_id}", response_model=schemas.PatientSchema, tags=["Patients"])
def get_patient_by_id(patient_id: int, db: Session = Depends(get_db)):
    pat = db.query(models.PatientModel).filter(models.PatientModel.id == patient_id).first()
    if not pat:
        raise HTTPException(status_code=404, detail="Patient not found")
    res = schemas.PatientSchema.from_orm(pat)
    res.id = str(pat.id)
    return res

@app.put("/patients/{patient_id}", response_model=schemas.PatientSchema, tags=["Patients"])
def update_patient(patient_id: int, pat_update: schemas.PatientUpdateSchema, db: Session = Depends(get_db)):
    db_pat = db.query(models.PatientModel).filter(models.PatientModel.id == patient_id).first()
    if not db_pat:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = pat_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pat, key, value)

    db.commit()
    db.refresh(db_pat)
    res = schemas.PatientSchema.from_orm(db_pat)
    res.id = str(db_pat.id)
    return res

@app.delete("/patients/{patient_id}", tags=["Patients"])
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_pat = db.query(models.PatientModel).filter(models.PatientModel.id == patient_id).first()
    if not db_pat:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(db_pat)
    db.commit()
    return {"status": "success", "message": f"Patient ID {patient_id} deleted"}

# =========================================================
# 6. APPOINTMENTS CRUD
# =========================================================
@app.post("/appointments", response_model=schemas.AppointmentSchema, tags=["Appointments"])
def create_appointment(app_data: schemas.AppointmentSchema, db: Session = Depends(get_db)):
    db_app = models.AppointmentModel(**app_data.dict(exclude={"id"}))
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    app_data.id = str(db_app.id)
    return app_data

@app.get("/appointments", response_model=List[schemas.AppointmentSchema], tags=["Appointments"])
def get_all_appointments(db: Session = Depends(get_db)):
    apps = db.query(models.AppointmentModel).all()
    res = []
    for a in apps:
        a_schema = schemas.AppointmentSchema.from_orm(a)
        a_schema.id = str(a.id)
        res.append(a_schema)
    return res

@app.get("/appointments/{appointment_id}", response_model=schemas.AppointmentSchema, tags=["Appointments"])
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db)):
    app_item = db.query(models.AppointmentModel).filter(models.AppointmentModel.id == appointment_id).first()
    if not app_item:
        raise HTTPException(status_code=404, detail="Appointment not found")
    res = schemas.AppointmentSchema.from_orm(app_item)
    res.id = str(app_item.id)
    return res

@app.put("/appointments/{appointment_id}", response_model=schemas.AppointmentSchema, tags=["Appointments"])
def update_appointment(appointment_id: int, app_update: schemas.AppointmentUpdateSchema, db: Session = Depends(get_db)):
    db_app = db.query(models.AppointmentModel).filter(models.AppointmentModel.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")

    update_data = app_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_app, key, value)

    db.commit()
    db.refresh(db_app)
    res = schemas.AppointmentSchema.from_orm(db_app)
    res.id = str(db_app.id)
    return res

@app.delete("/appointments/{appointment_id}", tags=["Appointments"])
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.AppointmentModel).filter(models.AppointmentModel.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(db_app)
    db.commit()
    return {"status": "success", "message": f"Appointment ID {appointment_id} deleted"}

# =========================================================
# 7. QUEUE TOKENS CRUD
# =========================================================
@app.post("/queue-tokens", response_model=schemas.QueueTokenSchema, tags=["Queue Tokens"])
def create_queue_token(token: schemas.QueueTokenSchema, db: Session = Depends(get_db)):
    db_token = models.QueueTokenModel(**token.dict(exclude={"tokenId"}))
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    token.tokenId = str(db_token.tokenId)
    return token

@app.get("/queue-tokens", response_model=List[schemas.QueueTokenSchema], tags=["Queue Tokens"])
def get_all_queue_tokens(db: Session = Depends(get_db)):
    tokens = db.query(models.QueueTokenModel).all()
    res = []
    for t in tokens:
        t_schema = schemas.QueueTokenSchema.from_orm(t)
        t_schema.tokenId = str(t.tokenId)
        res.append(t_schema)
    return res

@app.get("/queue-tokens/{token_id}", response_model=schemas.QueueTokenSchema, tags=["Queue Tokens"])
def get_queue_token_by_id(token_id: int, db: Session = Depends(get_db)):
    token = db.query(models.QueueTokenModel).filter(models.QueueTokenModel.tokenId == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    res = schemas.QueueTokenSchema.from_orm(token)
    res.tokenId = str(token.tokenId)
    return res

@app.put("/queue-tokens/{token_id}", response_model=schemas.QueueTokenSchema, tags=["Queue Tokens"])
def update_queue_token(token_id: int, token_update: schemas.QueueTokenUpdateSchema, db: Session = Depends(get_db)):
    db_token = db.query(models.QueueTokenModel).filter(models.QueueTokenModel.tokenId == token_id).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")

    update_data = token_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_token, key, value)

    db.commit()
    db.refresh(db_token)
    res = schemas.QueueTokenSchema.from_orm(db_token)
    res.tokenId = str(db_token.tokenId)
    return res

@app.delete("/queue-tokens/{token_id}", tags=["Queue Tokens"])
def delete_queue_token(token_id: int, db: Session = Depends(get_db)):
    db_token = db.query(models.QueueTokenModel).filter(models.QueueTokenModel.tokenId == token_id).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    db.delete(db_token)
    db.commit()
    return {"status": "success", "message": f"Token ID {token_id} deleted"}
