from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

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

class ScheduleModel(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    doctorId = Column(String(50))
    availableDate = Column(String(50))
    startTime = Column(String(50))
    endTime = Column(String(50))
    maxPatients = Column(Integer, default=10)

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