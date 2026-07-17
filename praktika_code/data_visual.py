"""Задание № 3: улучшенная визуализация числовых и категориальных данных."""
from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

import dataset

MARKER = "*"
DEFAULT_CMAP = "PuBuGn"
CMAPS = [
    "viridis", "plasma", "inferno", "magma", "cividis", "Greys", "Purples",
    "Blues", "Greens", "Oranges", "Reds", "YlOrBr", "YlOrRd", "OrRd",
    "PuRd", "RdPu", "BuPu", "GnBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn",
    "YlGn", "binary", "gist_yarg", "spring", "summer", "autumn", "winter",
]


class VisualApp:
    """Окно приложения для построения пяти типов диаграмм."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Улучшенная визуализация данных")
        self.root.minsize(1000, 650)

        self.df = dataset.df
        self.numeric = dataset.numeric_columns(self.df)
        self.categorical = dataset.categorical_columns(self.df)
        self.columns = list(self.df.columns)

        if len(self.numeric) < 2:
            messagebox.showerror("Ошибка", "Необходимо минимум две счётные колонки.")
            self.root.destroy()
            return

        self.x_column = self.numeric[0]
        self.y_column = self.numeric[1]
        self.cmap_name = tk.StringVar(value=DEFAULT_CMAP)

        self._build_interface()
        self.draw_graph()

    def _build_interface(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=6, pady=6)

        tk.Label(top, text="Цветовая схема:").pack(side=tk.LEFT)
        cmap_box = ttk.Combobox(
            top,
            textvariable=self.cmap_name,
            values=CMAPS,
            state="readonly",
            width=14,
        )
        cmap_box.pack(side=tk.LEFT, padx=5)
        cmap_box.bind("<<ComboboxSelected>>", lambda _event: self.draw_graph())

        tk.Button(top, text="Сохранить", command=self.save_graph).pack(side=tk.RIGHT)

        left = tk.LabelFrame(self.root, text="Ось Y")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)
        for column in self.columns:
            tk.Button(
                left,
                text=column,
                command=lambda c=column: self.select_y(c),
            ).pack(fill=tk.X, padx=3, pady=1)

        center = tk.Frame(self.root)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=center)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom = tk.LabelFrame(center, text="Ось X")
        bottom.pack(fill=tk.X, padx=6, pady=6)
        for column in self.columns:
            tk.Button(
                bottom,
                text=column,
                command=lambda c=column: self.select_x(c),
            ).pack(side=tk.LEFT, padx=1, pady=2)

    def is_numeric(self, column: str) -> bool:
        return column in self.numeric

    def is_categorical(self, column: str) -> bool:
        return column in self.categorical

    def select_x(self, column: str) -> None:
        self.x_column = column
        self.draw_graph()

    def select_y(self, column: str) -> None:
        self.y_column = column
        self.draw_graph()

    def palette(self, count: int) -> np.ndarray:
        """Возвращает хорошо различимые оттенки выбранной цветовой схемы.

        Начало последовательных палитр Matplotlib часто почти белое. Поэтому
        самый светлый участок намеренно пропускается. Для одного объекта берётся
        насыщенный оттенок из середины-тёмной части палитры.
        """
        cmap = matplotlib.colormaps[self.cmap_name.get()]
        if count <= 1:
            return np.asarray([cmap(0.72)])
        return cmap(np.linspace(0.28, 0.92, count))

    def draw_graph(self) -> None:
        self.axes.clear()

        x = self.x_column
        y = self.y_column
        x_num = self.is_numeric(x)
        y_num = self.is_numeric(y)
        x_cat = self.is_categorical(x)
        y_cat = self.is_categorical(y)

        if x == y and x_num:
            self._draw_histogram(x)
        elif x == y and x_cat:
            self._draw_pie(x)
        elif x_cat and y_num:
            self._draw_bar(x)
        elif x_num and y_cat:
            self._draw_boxplot(x, y)
        elif x_num and y_num:
            self._draw_scatter(x, y)
        else:
            self._draw_bar(x)

        self.axes.grid(True, alpha=0.25)
        self.figure.tight_layout()
        self.canvas.draw()

    def _draw_histogram(self, column: str) -> None:
        values = self.df[column].dropna()
        _counts, _bins, patches = self.axes.hist(
            values,
            bins=10,
            edgecolor="black",
            linewidth=1.0,
        )

        # Каждый столбец получает свой оттенок PuBuGn или выбранной палитры.
        for patch, color in zip(patches, self.palette(len(patches))):
            patch.set_facecolor(color)

        self.axes.set_xlabel(column)
        self.axes.set_ylabel("Количество")
        self.axes.set_title(f"Гистограмма распределения: {column}")

    def _draw_pie(self, column: str) -> None:
        counts = self.df[column].fillna("Нет данных").astype(str).value_counts()
        self.axes.pie(
            counts.values,
            labels=counts.index,
            colors=self.palette(len(counts)),
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1.0},
        )
        self.axes.set_title(f"Круговая диаграмма: {column}")

    def _draw_bar(self, column: str) -> None:
        counts = self.df[column].fillna("Нет данных").astype(str).value_counts()
        colors = self.palette(len(counts))
        self.axes.bar(
            counts.index,
            counts.values,
            color=colors,
            edgecolor="black",
            linewidth=0.8,
        )
        self.axes.set_xlabel(column)
        self.axes.set_ylabel("Количество записей")
        self.axes.set_title(f"Столбчатая диаграмма по категориям: {column}")
        self.axes.tick_params(axis="x", labelrotation=45)

    def _draw_boxplot(self, numeric_column: str, category_column: str) -> None:
        prepared = self.df[[numeric_column, category_column]].dropna()
        groups = list(prepared.groupby(category_column, sort=False)[numeric_column])

        if not groups:
            self.axes.text(
                0.5,
                0.5,
                "Нет данных для построения",
                ha="center",
                va="center",
                transform=self.axes.transAxes,
            )
            return

        labels = [str(name) for name, _values in groups]
        values = [group.to_numpy() for _name, group in groups]
        boxes = self.axes.boxplot(
            values,
            tick_labels=labels,
            patch_artist=True,
            medianprops={"color": "black", "linewidth": 1.5},
            whiskerprops={"color": "black"},
            capprops={"color": "black"},
        )

        for patch, color in zip(boxes["boxes"], self.palette(len(boxes["boxes"]))):
            patch.set_facecolor(color)
            patch.set_edgecolor("black")
            patch.set_alpha(0.95)

        self.axes.set_xlabel(category_column)
        self.axes.set_ylabel(numeric_column)
        self.axes.set_title(
            f"Коробочная диаграмма: {numeric_column} по {category_column}"
        )
        self.axes.tick_params(axis="x", labelrotation=45)

    def _draw_scatter(self, x_column: str, y_column: str) -> None:
        data = self.df[[x_column, y_column]].dropna()
        color = self.palette(1)[0]
        self.axes.scatter(
            data[x_column],
            data[y_column],
            marker=MARKER,
            color=color,
            edgecolors="black",
            linewidths=0.45,
            alpha=0.9,
        )
        self.axes.set_xlabel(x_column)
        self.axes.set_ylabel(y_column)
        self.axes.set_title(f"Точечная диаграмма: {y_column} от {x_column}")

    def save_graph(self) -> None:
        filename = datetime.now().strftime("graph%H_%M_%S.png")
        self.figure.savefig(filename, dpi=150, bbox_inches="tight")
        messagebox.showinfo("Сохранение", f"График сохранён в файл {filename}")


def main() -> None:
    root = tk.Tk()
    VisualApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
