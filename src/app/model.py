from pydantic import BaseModel, Field, EmailStr
import datetime


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


