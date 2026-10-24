from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import ReviewCreate, ReviewResponse, ReviewUpdate

router = APIRouter()

@router.get("", response_model=list[ReviewResponse])
async def get_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Review)
        .options(selectinload(models.Review.name))
        .order_by(models.Review.date_reviewed.desc())
    )
    reviews = result.scalars().all()
    return reviews

@router.post(
        "",
          response_model=ReviewResponse,
          status_code=status.HTTP_201_CREATED,
)
async def create_review(review: ReviewCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == review.user_id))
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
    await db.commit()
    await db.refresh(new_review, attribute_names=["name"])
    return new_review



@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Review)
        .options(selectinload(models.Review.name))
        .where(models.Review.id == review_id))
    review = result.scalars().first()
    if  review:
        return review
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")



@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review_full(
    review_id: int,
    review_data: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    if review_data.user_id != review.user_id:
        result = await db.execute(
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
    await db.commit()
    await db.refresh(review, attribute_names=["name"])
    return review




@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review_partial(
    review_id: int,
    review_data: ReviewUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    await db.commit()
    await db.refresh(review, attribute_names=["name"])
    return review



@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    await db.delete(review)
    await db.commit()
