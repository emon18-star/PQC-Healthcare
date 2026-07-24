from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str
    password: str
    role: str