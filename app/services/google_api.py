from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = '%Y/%m/%d %H:%M:%S'
ROW_COUNT = 100
COLUMN_COUNT = 11
SHEET_STRUCTURE = {
    'properties': {
        'title': 'Отчет на {}',
        'locale': 'ru_RU'
    },
    'sheets': [{
        'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': 'Лист1',
            'gridProperties': {
                'rowCount': ROW_COUNT,
                'columnCount': COLUMN_COUNT
            }
        }
    }]
}

TABLE_VALUES = [
    ['Отчет от', '{}'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    spreadsheet_body = SHEET_STRUCTURE.copy()
    spreadsheet_body['properties']['title'] = spreadsheet_body['properties']['title'].format(now_date_time)

    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


def format_project_data(res):
    duration = res.close_date - res.create_date
    days = duration.days
    seconds = duration.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    duration_str = f'{days} day, {hours}:{minutes:02}:{seconds}.{duration.microseconds // 1000:03}'

    return str(res.name), duration_str, str(res.description)


def get_column_letter(column_number):
    assert 1 <= column_number <= 26
    return chr(64 + column_number)


def get_spreadsheet_range(table_values):
    num_rows = len(table_values)
    num_columns = len(table_values[2])

    last_column_letter = get_column_letter(num_columns)
    return f'A1:{last_column_letter}{num_rows}'


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields='id'
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        all_projects: list,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')

    header = [row.copy() for row in TABLE_VALUES]
    header[0][1] = now_date_time
    all_projects.sort(key=lambda res: res.close_date - res.create_date)

    table_values = [
        *header,
        *[list(map(str, format_project_data(res))) for res in all_projects]
    ]

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    range_value = get_spreadsheet_range(table_values)
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=range_value,
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
