import io
from typing import Dict, List, Any

import xlsxwriter


def create_xls_analytics(
    data: Dict[str, List[Dict[str, Any]]],
    header_format_data: Dict[str, Any],
    headers: List[str]
) -> io.BytesIO:
    """Создает Excel-файл с аналитическими данными"""
    # Создаем Excel-файл в памяти
    output = io.BytesIO()
    xlsx_file = xlsxwriter.Workbook(output, {'in_memory': True})

    # Определяем формат заголовка
    header_format = xlsx_file.add_format(header_format_data)

    for model, versions in data.items():
        # Добавляем новый лист для модели
        worksheet = xlsx_file.add_worksheet(model)

        # Записываем заголовки столбцов
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        # Записываем данные поверсионно
        for row_num, version_data in enumerate(versions, start=1):
            worksheet.write(row_num, 0, model)
            worksheet.write(row_num, 1, version_data['version'])
            worksheet.write(row_num, 2, version_data['count'])

        # Устанавливаем ширину столбцов
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 25)

    # Закрываем файл
    xlsx_file.close()
    # Сбрасываем указатель потока на начало
    output.seek(0)

    return output
