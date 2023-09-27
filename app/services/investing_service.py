from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.donation import donation_crud


def calculate_balances(project, donation):
    balance_project = project.full_amount - project.invested_amount
    balance_donation = donation.full_amount - donation.invested_amount
    return balance_project, balance_donation


def process_investment(project, donation, balance_project, balance_donation):
    if balance_project > balance_donation:
        project.invested_amount += balance_donation
        donation.invested_amount += balance_donation
        donation.fully_invested = True
        donation.close_date = datetime.utcnow()
    elif balance_project <= balance_donation:
        project.invested_amount += min(balance_project, balance_donation)
        donation.invested_amount += min(balance_project, balance_donation)
        project.fully_invested = True
        project.close_date = datetime.utcnow()
        if balance_project == balance_donation:
            donation.fully_invested = True
            donation.close_date = datetime.utcnow()

    return project, donation


async def invest_in_projects(session: AsyncSession, object):
    while True:
        project, donation = await donation_crud.get_open_object(session)
        if not project or not donation:
            await session.commit()
            await session.refresh(object)
            return object

        balance_project, balance_donation = calculate_balances(project, donation)
        project, donation = process_investment(
            project,
            donation,
            balance_project,
            balance_donation
        )

        session.add(project)
        session.add(donation)
        await session.commit()
        await session.refresh(project)
        await session.refresh(donation)
