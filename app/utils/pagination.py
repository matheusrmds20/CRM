from typing import TypeVar
from sqlalchemy.orm import Query

from app.schemas.pagination import PaginationResponse

T = TypeVar("T")

def paginate(query: Query[T],
             page: int = 1,
             page_size: int = 10,
             ) -> PaginationResponse[T]:

    page = max(1, page)
    page_size = max(1, min(100, page_size))

    total = query.count()

    total_pages = (total + page_size - 1) // page_size

    # Ajusta page caso ultrapasse o total de páginas
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * page_size

    items = query.offset(offset).limit(page_size).all()

    return PaginationResponse(
        items=items,
        total=total,
        page=page,
        pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
