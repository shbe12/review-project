from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import ReviewCreate, ReviewResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

reviews: list[dict] = [
      {
          "id": 1,
          "name": "John Smith",
          "rating": 5,
          "activity": "Hiking",
          "comment": "The trail was beautiful and the scenery was amazing!",
          "date_reviewed": "April 20, 2025",
     },
      {
          "id": 2,
          "name": "Jane Doe",
          "rating": 4,
          "activity": "Kayaking",
          "comment": "It was a lot of fun and very relaxing. The water was beautiful.",
          "date_reviewed": "April 21, 2025",
      },
  ]


# @app.get("/")
# def home():
#     return {"message": "Hello World!"}

@app.get("/", include_in_schema=False, name="home")
@app.get("/reviews", include_in_schema=False, name="reviews")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"reviews": reviews, "title": "Home"},
        )

@app.get("/reviews/{review_id}", include_in_schema=False)
def review_page(request: Request, review_id: int):
    for review in reviews:
        if review.get("id") == review_id:
            activity = review["activity"][:50]
            return templates.TemplateResponse(
                request,
                "review.html",
                {"review": review, "title": activity},
                )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")


@app.get("/api/reviews", response_model=list[ReviewResponse])
def get_reviews():
    return reviews

@app.post(
        "/api/reviews",
          response_model=ReviewResponse,
          status_code=status.HTTP_201_CREATED,
)
def create_review(review: ReviewCreate):
    new_review = max(p["id"] for p in reviews) + 1 if reviews else 1
    new_review = {
        "id": new_review,
        "name": review.name,
        "rating": review.rating,
        "activity": review.activity,
        "comment": review.comment,
        "date_reviewed": "April 22, 2025",
    }
    reviews.append(new_review)
    return new_review


@app.get("/api/reviews/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int):
    for review in reviews:
        if review.get("id") == review_id:
            return review
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

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
