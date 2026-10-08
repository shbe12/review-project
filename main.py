from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/reviews", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{reviews[0]['title']}</h1>"


@app.get("/api/reviews")
def get_reviews():
    return reviews
