from pydantic import BaseModel, ConfigDict, Field

class ReviewBase(BaseModel):
    activity: str = Field(min_length=1, max_length=100)
    comment:  str = Field(min_length=1, max_length=500)
    name: str = Field(min_length=1, max_length=100)
    rating: int = Field(ge=1, le=5)


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date_reviewed: str
