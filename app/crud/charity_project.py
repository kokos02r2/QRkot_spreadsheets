from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
            project: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project
            )
        )
        return db_project_id.scalars().first()

    async def get_project_invested_amount_by_project_id(
            self,
            project_id: int,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_invested_amount = await session.execute(
            select(CharityProject.invested_amount).where(
                CharityProject.id == project_id
            )
        )
        return db_project_invested_amount.scalars().first()

    async def get_project_full_amount_by_project_id(
            self,
            project_id: int,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_full_amount = await session.execute(
            select(CharityProject.full_amount).where(
                CharityProject.id == project_id
            )
        )
        return db_project_full_amount.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ):
        db_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested
            )
        )
        return db_projects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
