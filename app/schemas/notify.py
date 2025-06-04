from pydantic import BaseModel

class NotificationCreate(BaseModel):
    recipient: str
    message: str

class NotificationOut(BaseModel):
    id: int
    recipient: str
    message: str
    status: str

    class Config:
        # Pydantic v2: use 'from_attributes' instead of deprecated 'orm_mode'
        from_attributes = True
