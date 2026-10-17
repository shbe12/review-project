from datetime import datetime
from pydantic import BaseModel, ConfigDict,EmailStr, Field



class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_file: str | None
    image_path: str


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None, min_length=1, max_length=200)


class ReviewBase(BaseModel):
    activity: str = Field(min_length=1, max_length=100)
    comment:  str = Field(min_length=1, max_length=500)
    rating: int = Field(ge=1, le=5)


class ReviewCreate(ReviewBase):
    user_id: int #TEMPORARY: This will be replaced with the current user ID from the session

class ReviewUpdate(BaseModel):
    activity: str | None = Field(default=None, min_length=1, max_length=100)
    comment:  str | None= Field(default=None, min_length=1, max_length=500)
    rating: int | None = Field(default=None, ge=1, le=5)


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    date_reviewed: datetime
    name: UserResponse
