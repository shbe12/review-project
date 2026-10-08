from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

reviews: list[dict] = [
      {
          "id": 1,
          "name": "John Smith",
          "rating": 5,
          "title": "Hiking",
          "comment": "The trail was beautiful and the scenery was amazing!",
          "date_reviewed": "April 20, 2025",
     },
      {
          "id": 2,
          "name": "Jane Doe",
          "rating": 4,
          "title": "Kayaking",
          "comment": "It was a lot of fun and very relaxing. The water was beautiful.",
          "date_reviewed": "April 21, 2025",
      },
  ]


# @app.get("/")
# def home():
#     return {"message": "Hello World!"}

@app.get("/", include_in_schema=False)
@app.get("/reviews", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request,"home.html", {"reviews": reviews, "title": "Home"})


@app.get("/api/reviews")
def get_reviews():
    return reviews
