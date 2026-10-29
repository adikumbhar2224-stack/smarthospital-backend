from pydantic import BaseModel
from typing import Optional, List

class LoginRequest(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    password: str

class LoginResponse(BaseModel):
    status: str
    message: str
    user_id: str
    role: str

class UserSchema(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    role: str
    phone: str
    email: Optional[str] = None

    class Config:
        from_attributes = True

class DepartmentSchema(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class DoctorSchema(BaseModel):
    id: Optional[str] = None
    name: str
    department: str
    phone: Optional[str] = None
    email: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[str] = None

    class Config:
        from_attributes = True

class PatientSchema(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    patient_name: Optional[str] = None
    fullName: Optional[str] = None
    age: int
    gender: str
    phone: str
    email: Optional[str] = None
    department_id: Optional[int] = None
    doctor_id: Optional[int] = None

    class Config:
        from_attributes = True

class ScheduleSchema(BaseModel):
    id: Optional[str] = None
    doctorId: str
    availableDate: str
    startTime: str
    endTime: str
    maxPatients: Optional[int] = 10

    class Config:
        from_attributes = True

class AppointmentSchema(BaseModel):
    id: Optional[str] = None
    patientId: str
    doctorId: str
    departmentId: str
    appointmentDate: str
    appointmentTime: str
    status: Optional[str] = "Pending"

    class Config:
        from_attributes = True

class QueueTokenSchema(BaseModel):
    tokenId: Optional[str] = None
    appointmentId: Optional[str] = None
    patientId: str
    tokenNumber: Optional[int] = None
    patientName: str
    department: str
    doctorName: str
    status: Optional[str] = "Waiting"

    class Config:
        from_attributes = True