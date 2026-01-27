from fastapi import APIRouter
from .students import router as students_router
from .exams import router as exams_router
from .grades import router as grades_router

api_router = APIRouter()

api_router.include_router(students_router)
api_router.include_router(exams_router)
api_router.include_router(grades_router)

__all__ = ["api_router"]