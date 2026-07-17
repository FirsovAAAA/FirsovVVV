"""Задание № 1: подготовка данных к работе.

При импорте модуль только загружает dataset.csv в глобальную переменную ``df``.
При прямом запуске формирует распечатки в консоли и дублирует их в report.txt.
"""
from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"
REPORT_PATH = BASE_DIR / "report.txt"

if not DATASET_PATH.exists():
    raise FileNotFoundError(f"Не найден файл датасета: {DATASET_PATH}")

df = pd.read_csv(DATASET_PATH)

# Классификация выполнена по смыслу данных варианта 20.
# Идентификатор, тональность, лад и музыкальный размер являются категориями,
# даже когда хранятся числами: их сложение не имеет содержательного смысла.
CATEGORICAL_COLUMNS = [
    "Unnamed: 0",
    "title",
    "artist/s",
    "key",
    "mode",
    "time_signature",
]
COUNTABLE_COLUMNS = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "valence",
    "tempo",
    "duration_ms",
]


def categorical_columns(data: pd.DataFrame | None = None) -> list[str]:
    """Вернуть существующие в DataFrame категориальные колонки."""
    data = df if data is None else data
    return [name for name in CATEGORICAL_COLUMNS if name in data.columns]


def numeric_columns(data: pd.DataFrame | None = None) -> list[str]:
    """Вернуть существующие счётные числовые колонки."""
    data = df if data is None else data
    return [
        name
        for name in COUNTABLE_COLUMNS
        if name in data.columns and pd.api.types.is_numeric_dtype(data[name])
    ]


def build_report(data: pd.DataFrame | None = None) -> str:
    """Сформировать полный текст статистического отчёта."""
    data = df if data is None else data
    output = StringIO()

    # Количество строк и колонок.
    print(data.shape, file=output)

    # Стандартная распечатка DataFrame.info().
    info_buffer = StringIO()
    data.info(buf=info_buffer)
    print(info_buffer.getvalue(), file=output, end="")

    # Число пропусков во всех колонках, включая нулевые значения.
    print(data.isna().sum().to_string(), file=output)

    # Базовая статистика счётных колонок.
    print("Колонка> среднее; медиана; отклонение", file=output)
    for column in numeric_columns(data):
        series = data[column]
        print(
            f"{column}> {series.mean():.2f}; {series.median():.2f}; {series.std():.2f}",
            file=output,
        )

    # Частотные распределения категориальных колонок.
    for column in categorical_columns(data):
        print(f"\n{column}", file=output)
        print(data[column].value_counts(dropna=False).to_string(), file=output)
        print("Name: count, dtype: int64", file=output)

    return output.getvalue()


def main() -> None:
    report = build_report()
    print(report, end="")
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nОтчёт сохранён: {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
