from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PaginationResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int
    has_next: bool
    has_previous: bool

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)