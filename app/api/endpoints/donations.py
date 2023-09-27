from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donations import DonationAdminDB, DonationCreate, DonationDB
from app.services.investing_service import invest_in_projects

router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)],
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Создание нового пожертвования."""
    new_donation = await donation_crud.create(
        donation, session, user
    )
    await invest_in_projects(session, new_donation)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationAdminDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
) -> list[str]:
    """Получает список всех пожертвований."""
    return await donation_crud.get_multi(session)


@router.get(
    '/my', response_model=list[DonationDB],
    dependencies=[Depends(current_user)],
)
async def get_my_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
) -> list[str]:
    """Получает список всех пожертвований для текущего пользователя."""
    return await donation_crud.get_by_user(
        session=session, user=user
    )
