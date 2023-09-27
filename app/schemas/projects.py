from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

MIN_LENGTH = 1
MAX_LENGHT = 100


class CharityBase(BaseModel):
    name: str = Field(..., min_length=MIN_LENGTH, max_length=MAX_LENGHT)
    description: str = Field(..., min_length=MIN_LENGTH)
    full_amount: PositiveInt

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityBase):
    pass


class CharityProjectUpdate(CharityBase):
    name: Optional[str] = Field(None, min_length=MIN_LENGTH, max_length=MAX_LENGHT)
    description: Optional[str] = Field(None, min_length=MIN_LENGTH)
    full_amount: Optional[PositiveInt]


class CharityProjectDB(CharityBase):
    id: int
    invested_amount: int = 0
    fully_invested: bool = False
    create_date: datetime
    close_date: datetime = None

    class Config:
        orm_mode = True
