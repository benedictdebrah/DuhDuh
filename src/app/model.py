from pydantic import BaseModel, Field, EmailStr


class PostSchema(BaseModel):
    title : str = Field(...)
    content : str = Field(...)

    class Config:
        json_schema_extra = {
            "example" :{
                "title" : "Checking my knowledge on authentication",
                "content" : "Let's"
            }
        }

class UserSchema(BaseModel):
    first_name : str = Field(...)
    last_name : str = Field(...)
    email : EmailStr = Field(...)
    password : str = Field(...)

    class Config:
        json_schema_extra = {
            "example" :{
                "first_name" : "Benedict",
                "last_name" : "Debrah",
                "email" : "benedict@fastapi.com",
                "password": "extraordinary"
            }
        }

class UserLoginSchema(BaseModel):
    email : EmailStr = Field(...)
    password : str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "benedict@fastapi.com",
                "password": "weakpassword"
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str