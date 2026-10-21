from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import ReviewResponse, UserCreate,UserResponse, UserUpdate

router = APIRouter(
