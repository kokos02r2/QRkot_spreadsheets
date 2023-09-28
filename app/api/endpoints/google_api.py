from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.schemas.projects import CharityProjectDB
from app.crud.charity_project import charity_project_crud
from app.services.google_api import (
    spreadsheets_create,
    set_user_permissions,
    spreadsheets_update_value
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    dependencies=[Depends(current_superuser)]
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    closed_projects = await charity_project_crud.get_projects_by_completion_rate(session)

    try:
        spreadsheetid = await spreadsheets_create(wrapper_services)
    except Exception as e:
        # Логирование ошибки
        print(f"Ошибка при создании таблицы в Google Sheets: {e}")
        return {"error": "Произошла ошибка при создании таблицы в Google Sheets"}

    try:
        await set_user_permissions(spreadsheetid, wrapper_services)
    except Exception as e:
        # Логирование ошибки
        print(f"Ошибка при установке прав доступа к таблице: {e}")
        return {"error": "Произошла ошибка при установке прав доступа к таблице"}

    try:
        await spreadsheets_update_value(spreadsheetid, closed_projects, wrapper_services)
    except Exception as e:
        # Логирование ошибки
        print(f"Ошибка при обновлении данных в таблице: {e}")
        return {"error": "Произошла ошибка при обновлении данных в таблице"}

    return closed_projects
