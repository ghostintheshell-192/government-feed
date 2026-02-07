"""Dependency injection helpers for FastAPI."""

from backend.src.infrastructure.database import get_db
from backend.src.infrastructure.unit_of_work import UnitOfWork
from fastapi import Depends
from sqlalchemy.orm import Session


def get_unit_of_work(db: Session = Depends(get_db)) -> UnitOfWork:
    """
    Create and return a Unit of Work instance.

    Args:
        db: Database session from FastAPI dependency injection

    Returns:
        UnitOfWork instance with access to all repositories
    """
    return UnitOfWork(db)
