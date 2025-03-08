from typing import Generic, List, Optional, TypeVar

from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar("T")  # Generic Type Variable for any response model


class PaginatedResponse(BaseModel, Generic[T]):
    """A response model for paginated results."""

    total_count: int
    total_pages: int
    page: int
    page_size: int
    next_page: Optional[str]
    previous_page: Optional[str]
    results: List[T]  # This allows storing any response type


T = TypeVar("T")


def paginate(
    query: Query, page: int, page_size: int, request: Request
) -> PaginatedResponse[T]:
    """
    Generic pagination function for SQLAlchemy queries.

    :param query: SQLAlchemy Query object
    :param page: Current page number
    :param page_size: Number of records per page
    :param request: FastAPI request object (for generating URLs)
    :return: PaginatedResponse with generic results
    """
    total_count = query.count()
    total_pages = (
        total_count + page_size - 1
    ) // page_size  # Ceiling division

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse[T](
        total_count=total_count,
        total_pages=total_pages,
        page=page,
        page_size=page_size,
        next_page=_get_next_page_url(request, page, total_pages, page_size),
        previous_page=_get_previous_page_url(request, page, page_size),
        results=items,
    )


def _get_next_page_url(
    request: Request, page: int, total_pages: int, page_size: int
) -> Optional[str]:
    """Generates the next page URL if available."""
    if page < total_pages:
        return str(
            request.url.include_query_params(
                page=page + 1, page_size=page_size
            )
        )
    return None


def _get_previous_page_url(
    request: Request, page: int, page_size: int
) -> Optional[str]:
    """Generates the previous page URL if available."""
    if page > 1:
        return str(
            request.url.include_query_params(
                page=page - 1, page_size=page_size
            )
        )
    return None
