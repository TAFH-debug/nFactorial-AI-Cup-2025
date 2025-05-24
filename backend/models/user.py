from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    username: str
    password: str
    
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str = Field(index=True)

class UserCreate(UserBase):
    pass