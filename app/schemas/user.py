from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True

class UserInLoan(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

        