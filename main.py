from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import select

from sqlalchemy.orm import Session

import models
from database import Base, engine , get_db

from schemas import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")



@app.get("/", include_in_schema=False, name="home")
@app.get("/reviews", include_in_schema=False, name="reviews")
def home(request: Request,db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review))
    reviews = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"reviews": reviews, "title": "Home"},
        )


@app.get("/reviews/{review_id}", include_in_schema=False)
def review_page(request: Request, review_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if review:
       title = review.activity[:50]
       return templates.TemplateResponse(
            request,
                    "review.html",
                    {"review": review, "title": title},
                    )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")


@app.get("/users/{user_id}/reviews", include_in_schema=False, name="user_reviews")
def user_reviews_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Review).where(models.Review.user_id == user_id))
    reviews = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_reviews.html",
        {"reviews": reviews, "user": user, "title": f"{user.username}'s Reviews"},
    )

@app.post(
        "/api/users",
          response_model=UserResponse,
          status_code=status.HTTP_201_CREATED,
)

def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.username == user.username))

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = db.execute(
        select(models.User).where(models.User.email == user.email))

    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id))

    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )



@app.get("/api/users/{user_id}/reviews", response_model=list[ReviewResponse])
def get_user_reviews(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Review).where(models.Review.user_id == user_id))
    reviews = result.scalars().all()
    return reviews


@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_update.username is not None and user_update.username != user.username:
        result = db.execute(
            select(models.User).where(models.User.username == user_update.username)
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    if user_update.email is not None and user_update.email != user.email:
        result = db.execute(
            select(models.User).where(models.User.email == user_update.email)
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.image_file is not None:
        user.image_file = user_update.image_file

    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()


@app.get("/api/reviews", response_model=list[ReviewResponse])
def get_reviews(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review))
    reviews = result.scalars().all()
    return reviews

@app.post(
        "/api/reviews",
          response_model=ReviewResponse,
          status_code=status.HTTP_201_CREATED,
)
def create_review(review: ReviewCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == review.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_review =models.Review(
        activity=review.activity,
        comment=review.comment,
        rating=review.rating,
        user_id=review.user_id,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@app.get("/api/reviews/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if  review:
        return review
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")


@app.put("/api/reviews/{review_id}", response_model=ReviewResponse)
def update_review_full(
    review_id: int,
    review_data: ReviewCreate,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    if review_data.user_id != review.user_id:
        result = db.execute(
            select(models.User).where(models.User.id == review_data.user_id),
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
    review.activity = review_data.activity
    review.comment = review_data.comment
    review.rating = review_data.rating
    review.user_id = review_data.user_id
    db.commit()
    db.refresh(review)
    return review



@app.patch("/api/reviews/{review_id}", response_model=ReviewResponse)
def update_review_partial(
    review_id: int,
    review_data: ReviewUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review


@app.delete("/api/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    db.delete(review)
    db.commit()




@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request,exception: StarletteHTTPException,):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=exception.status_code,
                content={"detail": message},
            )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request,exception: RequestValidationError,):
    if request.url.path.startswith("/api"):
         return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        content={"detail": exception.errors()},
                    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
